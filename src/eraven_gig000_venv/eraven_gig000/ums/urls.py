# ums/urls.py

from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, ProfileViewSet, RoleViewSet, PermissionViewSet,
    CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView, UserRegistrationView,
    token_lifetime_view,
    CustomPasswordResetView, ActivateAccountView, ResendActivationEmailView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token-lifetime/', token_lifetime_view, name='token-lifetime'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Activation URL
    # path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('activate/<str:activation_id>/', ActivateAccountView.as_view(), name='activate'),
    path('resend-activation/', ResendActivationEmailView.as_view(), name='resend-activation'),

    # Password Reset URLs using Custom View
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