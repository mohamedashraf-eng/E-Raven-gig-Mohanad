from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile, Role, Permission

class UserManagementTests(APITestCase):
    def setUp(self):
        # Create roles, permissions, and users
        self.admin_role = Role.objects.create(name="Admin", description="Administrator role")
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword", role=self.admin_role
        )
        self.user_role = Role.objects.create(name="User", description="Regular user role")
        self.regular_user = User.objects.create_user(
            username="user", email="user@example.com", password="userpassword", role=self.user_role
        )
        
        # Obtain JWT token for the admin user
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(refresh.access_token)

    # Helper method to set authentication for requests
    def authenticate_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)

    def test_user_creation(self):
        self.authenticate_as_admin()
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'role': self.user_role.id  # Setting role as User
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(username='newuser').email, 'newuser@example.com')

    def test_user_list(self):
        self.authenticate_as_admin()
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # Should contain at least the admin user

    def test_profile_update(self):
        self.authenticate_as_admin()
        url = reverse('profile-detail', args=[self.regular_user.profile.id])
        data = {'bio': 'Updated bio', 'phone_number': '1234567890'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Profile.objects.get(user=self.regular_user).bio, 'Updated bio')

    def test_role_creation(self):
        self.authenticate_as_admin()
        url = reverse('role-list')
        data = {'name': 'Instructor', 'description': 'Instructor role'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.count(), 3)

    def test_permission_creation(self):
        self.authenticate_as_admin()
        url = reverse('permission-list')
        data = {'name': 'Can_View_Courses', 'description': 'Permission to view courses'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Permission.objects.count(), 1)

    def test_login_and_token_generation(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'admin', 'password': 'adminpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        # First, obtain a refresh token
        url = reverse('token_obtain_pair')
        data = {'username': 'admin', 'password': 'adminpassword'}
        response = self.client.post(url, data, format='json')
        refresh_token = response.data['refresh']

        # Use the refresh token to get a new access token
        url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_unauthenticated_user_access(self):
        # Test that an unauthenticated user cannot access the user list
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_access(self):
        # Login as a regular user and attempt to create a new user (should fail)
        refresh = RefreshToken.for_user(self.regular_user)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        url = reverse('user-list')
        data = {'username': 'unauthorized', 'email': 'unauthorized@example.com', 'password': 'password'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
