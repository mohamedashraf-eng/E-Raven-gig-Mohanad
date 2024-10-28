# ums/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, RoleViewSet, PermissionViewSet,
    CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView, UserRegistrationView,
    token_lifetime_view
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')

# Custom Routes
urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token-lifetime/', token_lifetime_view, name='token-lifetime'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
