from rest_framework import serializers
from .models import User, Profile, Role, Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.conf import settings

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'description']

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions']

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'is_staff']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # Set user as inactive until email confirmation
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'phone_number']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        # Add more claims if needed

        return token

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Custom serializer that reads the refresh token from a cookie instead of the request body.
    """

    def validate(self, attrs):
        request = self.context.get("request")
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

        if not refresh_token:
            raise serializers.ValidationError(
                {"detail": "Refresh token cookie not found."},
                code='authorization'
            )

        attrs['refresh'] = refresh_token
        return super().validate(attrs)
    