from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import User, Profile, Role, Permission
from .serializers import (
    UserSerializer, UserCreateSerializer, ProfileSerializer,
    RoleSerializer, PermissionSerializer
)
from .permissions import IsAdminOrReadOnly

class UserViewSet(viewsets.ModelViewSet):
    """
    User viewset that allows viewing, creating, and managing users.
    Non-admin users can only view users, while admin users can perform all actions.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_serializer_class(self):
        """Use a different serializer for user creation."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        """Optimize queryset based on the user's permissions."""
        if self.request.user.is_staff:
            return self.queryset  # Admins see all users
        return self.queryset.filter(id=self.request.user.id)  # Regular users see only their own details

    def perform_create(self, serializer):
        """Custom logic when creating a new user."""
        serializer.save()  # Additional logic can be added if needed (e.g., sending a welcome email)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Profile viewset that allows users to view and edit their own profile.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the profile related to the current user."""
        return Profile.objects.filter(user=self.request.user)


class RoleViewSet(viewsets.ModelViewSet):
    """
    Role viewset restricted to admin users, for managing user roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        """Custom save logic for roles, if needed."""
        serializer.save()  # Add additional logic here if needed


class PermissionViewSet(viewsets.ModelViewSet):
    """
    Permission viewset restricted to admin users, for managing permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        """Custom save logic for permissions, if needed."""
        serializer.save()  # Add additional logic here if needed
