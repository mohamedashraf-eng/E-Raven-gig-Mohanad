# ums/urls.py

from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, ProfileViewSet, RoleViewSet, PermissionViewSet,
    CustomTokenObtainPairView, CustomTokenRefreshView, token_lifetime_view,
    UserRegistrationView, UserProfileView, UserProfileEditView,
    LogoutView, ActivateAccountView, ResendActivationEmailView,
    CustomPasswordResetView
)

# DRF Router Configuration
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    # API Endpoints for Users, Profiles, Roles, Permissions
    path('', include(router.urls)),

    # Authentication Endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Token Lifetime Check
    path('token-lifetime/', token_lifetime_view, name='token-lifetime'),

    # User Registration and Activation
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('activate/<str:activation_id>/', ActivateAccountView.as_view(), name='activate'),
    path('resend-activation/', ResendActivationEmailView.as_view(), name='resend-activation'),

    # User Profile Management
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', UserProfileEditView.as_view(), name='edit_user_profile'),

    # Password Reset Endpoints
    path('password-reset/', CustomPasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
