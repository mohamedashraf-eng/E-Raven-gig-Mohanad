# ums/views.py

from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile, Role, Permission
from .serializers import (
    UserSerializer, UserCreateSerializer, ProfileSerializer,
    RoleSerializer, PermissionSerializer
)
from .permissions import IsAdminOrReadOnly
from django.http import JsonResponse
from datetime import timedelta

class UserViewSet(viewsets.ModelViewSet):
    """
    Allows viewing, creating, and managing users.
    Admins can manage all users, while regular users can only view themselves.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        return UserCreateSerializer if self.action == 'create' else UserSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset  # Admins see all users
        return self.queryset.filter(id=self.request.user.id)  # Regular users see only their own details

class ProfileViewSet(viewsets.ModelViewSet):
    """
    Allows authenticated users to view and edit their own profile.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

class RoleViewSet(viewsets.ModelViewSet):
    """
    Restricted to admins, for creating and managing user roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]

class PermissionViewSet(viewsets.ModelViewSet):
    """
    Restricted to admins, for creating and managing permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        password1 = data.get('password1')
        password2 = data.get('password2')

        if password1 != password2:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Add 'password' field with the value of password1 to satisfy serializer
        data['password'] = password1

        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Helper function to set JWT tokens as cookies
def set_auth_cookies(response, access_token=None, refresh_token=None):
    """Helper function to set access and refresh tokens as cookies."""
    if access_token:
        response.set_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE'],
            access_token,
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        )
    if refresh_token:
        response.set_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            refresh_token,
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        )
    return response

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining tokens and setting them in cookies.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh = RefreshToken(response.data['refresh'])
            response = set_auth_cookies(
                response,
                access_token=str(refresh.access_token),
                refresh_token=str(refresh),
            )
            # Remove tokens from response data to avoid redundant transfer
            response.data.pop('access', None)
            response.data.pop('refresh', None)
        return response

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for refreshing access tokens and updating the cookie.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data['access']
            response = set_auth_cookies(response, access_token=access_token)
            response.data.pop('access', None)
        return response

class LogoutView(APIView):
    """
    Logs out the user by deleting the authentication cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response({"message": "Logged out successfully"}, status=204)
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        return response

def token_lifetime_view(request):
    access_token_lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=15)).total_seconds()
    return JsonResponse({'access_token_lifetime': access_token_lifetime})