# ums/tests/test_views.py

from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from datetime import timedelta
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from ums.models import Profile, Role, Permission
from cms.models import Enrollment, UserProgress, Ranking, Course, Challenge, Workshop
from django.contrib.auth.tokens import default_token_generator
from django.core import mail

User = get_user_model()

class UMSViewsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the entire TestCase.
        """
        # Create roles
        cls.role_admin = Role.objects.create(name='Admin')
        cls.role_user = Role.objects.create(name='User')
        
        # Create permissions
        cls.permission_manage_users = Permission.objects.create(name='manage_users')
        cls.permission_manage_roles = Permission.objects.create(name='manage_roles')
        
        # Assign permissions to roles
        cls.role_admin.permissions.add(cls.permission_manage_users, cls.permission_manage_roles)
        
        # Create users
        cls.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            total_points=1000,
            role=cls.role_admin
        )
        
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            total_points=100,
            role=cls.role_user
        )
        
        cls.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='otherpassword',
            total_points=50,
            role=cls.role_user  # Assuming 'User' role
        )
        
        # Update profiles
        cls.user.profile.bio = 'Test bio'
        cls.user.profile.save()
        
        cls.other_user.profile.bio = 'Other bio'
        cls.other_user.profile.save()
        
        cls.admin_user.profile.bio = 'Admin bio'
        cls.admin_user.profile.save()
        
        # Create a course for enrollment tests
        cls.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            proficiency_level='beginner'
        )
        
        # Enroll user in the course
        cls.enrollment = Enrollment.objects.create(user=cls.user, course=cls.course)
        
        # Create a challenge
        cls.challenge = Challenge.objects.create(
            title='Test Challenge',
            course=cls.course,
            points=50,
            date=timezone.now().date()
        )
        
        # Create a workshop
        cls.workshop = Workshop.objects.create(
            title='Test Workshop',
            course=cls.course,
            points_cost=30,
            duration=timedelta(hours=1, minutes=30),
            date_time=timezone.now() + timedelta(days=1),
            meeting_link='http://example.com/workshop'
        )
        
        # Initialize rankings
        cls.user.ranking.points = 100
        cls.user.ranking.save()
        
        cls.other_user.ranking.points = 50
        cls.other_user.ranking.save()
    
    def setUp(self):
        """
        Set up before each test method.
        """
        self.client = APIClient()
        
        # Authenticate and obtain JWT tokens
        login_url = reverse('ums:token_obtain_pair')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, 200, "Authentication failed.")
        
        # Retrieve the access and refresh tokens
        self.access_token = response.data.get('access')
        self.refresh_token = response.data.get('refresh')
        self.assertIsNotNone(self.access_token, "Access token not found in authentication response.")
        self.assertIsNotNone(self.refresh_token, "Refresh token not found in authentication response.")
        
        # Set the tokens in cookies as per SIMPLE_JWT settings
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = self.access_token
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']] = self.refresh_token
    
    # ----------------------------
    # User Registration Tests
    # ----------------------------
    
    def test_user_registration_success(self):
        """
        Test that a user can successfully register.
        """
        registration_url = reverse('ums:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        }
        response = self.client.post(registration_url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/check_email.html')
        
        # Check that an activation email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Activate your account.', mail.outbox[0].subject)
        self.assertIn('newuser@example.com', mail.outbox[0].to)
        
        # Check that activation data is stored in cache
        activation_id = cache.get(f'activation_email_newuser@example.com')
        self.assertIsNotNone(activation_id)
        user_data = cache.get(f'activation_{activation_id}')
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['username'], 'newuser')
        self.assertEqual(user_data['email'], 'newuser@example.com')
    
    def test_user_registration_password_mismatch(self):
        """
        Test that registration fails if passwords do not match.
        """
        registration_url = reverse('ums:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'differentpassword',
        }
        response = self.client.post(registration_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Passwords do not match.', response.data['detail'])
        self.assertEqual(len(mail.outbox), 0)  # No email should be sent
    
    # ----------------------------
    # Account Activation Tests
    # ----------------------------
    
    def test_activate_account_success(self):
        """
        Test that a user can activate their account with a valid activation ID.
        """
        # First, register a new user to get activation_id
        registration_url = reverse('ums:register')
        data = {
            'username': 'activateuser',
            'email': 'activateuser@example.com',
            'password1': 'activatepassword123',
            'password2': 'activatepassword123',
        }
        response = self.client.post(registration_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        
        activation_id = cache.get('activation_email_activateuser@example.com')
        self.assertIsNotNone(activation_id)
        
        activate_url = reverse('ums:activate', kwargs={'activation_id': activation_id})
        response = self.client.get(activate_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/activate_account.html')
        
        # Check that the user is created and active
        user = User.objects.get(username='activateuser')
        self.assertTrue(user.is_active)
        
        # Check that activation data is cleared from cache
        self.assertIsNone(cache.get(f'activation_{activation_id}'))
        self.assertIsNone(cache.get('activation_email_activateuser@example.com'))
    
    def test_activate_account_invalid_id(self):
        """
        Test that activation fails with an invalid activation ID.
        """
        activate_url = reverse('ums:activate', kwargs={'activation_id': 'invalid-id'})
        response = self.client.get(activate_url)
        
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'registration/activation_invalid.html')
    
    # ----------------------------
    # Resend Activation Email Tests
    # ----------------------------
    
    def test_resend_activation_email_success(self):
        """
        Test that an activation email can be resent successfully.
        """
        # Register a new user
        registration_url = reverse('ums:register')
        data = {
            'username': 'resenduser',
            'email': 'resenduser@example.com',
            'password1': 'resendpassword123',
            'password2': 'resendpassword123',
        }
        response = self.client.post(registration_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        
        # Clear the mail outbox
        mail.outbox = []
        
        resend_url = reverse('ums:resend_activation')
        resend_data = {'email': 'resenduser@example.com'}
        response = self.client.post(resend_url, resend_data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Activation email resent', response.data['detail'])
        
        # Check that a new activation email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Activate your account.', mail.outbox[0].subject)
        self.assertIn('resenduser@example.com', mail.outbox[0].to)
    
    def test_resend_activation_email_no_pending_activation(self):
        """
        Test that resending activation email fails if no pending activation exists.
        """
        resend_url = reverse('ums:resend_activation')
        resend_data = {'email': 'nonexistent@example.com'}
        response = self.client.post(resend_url, resend_data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('No pending activation found', response.data['detail'])
        self.assertEqual(len(mail.outbox), 0)
    
    # ----------------------------
    # Authentication Tests
    # ----------------------------
    
    def test_login_success(self):
        """
        Test that a user can successfully log in and receive tokens.
        """
        login_url = reverse('ums:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(login_url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Check that tokens are set in cookies
        self.assertIn(settings.SIMPLE_JWT['AUTH_COOKIE'], response.cookies)
        self.assertIn(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'], response.cookies)
    
    def test_login_failure(self):
        """
        Test that login fails with incorrect credentials.
        """
        login_url = reverse('ums:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(login_url, data, format='json')
        
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
    
    def test_logout_authenticated(self):
        """
        Test that an authenticated user can successfully log out.
        """
        logout_url = reverse('ums:logout')
        response = self.client.get(logout_url)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pages:landing-page'))
        
        # Check that auth cookies are deleted
        self.assertEqual(response.cookies.get(settings.SIMPLE_JWT['AUTH_COOKIE']).value, '')
        self.assertEqual(response.cookies.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']).value, '')
    
    def test_logout_unauthenticated(self):
        """
        Test that an unauthenticated user attempting to log out is handled gracefully.
        """
        self.client.credentials()  # Remove authentication by clearing credentials
        logout_url = reverse('ums:logout')
        response = self.client.get(logout_url)
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    # ----------------------------
    # Password Reset Tests
    # ----------------------------
    
    def test_password_reset_success(self):
        """
        Test that a password reset email is sent successfully.
        """
        password_reset_url = reverse('password_reset')
        data = {'email': 'testuser@example.com'}
        response = self.client.post(password_reset_url, data)
        
        self.assertRedirects(response, reverse('password_reset_done'))
        
        # Check that a password reset email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset Requested', mail.outbox[0].subject)
        self.assertIn('testuser@example.com', mail.outbox[0].to)
    
    def test_password_reset_no_user(self):
        """
        Test that password reset fails if the email does not correspond to any user.
        """
        password_reset_url = reverse('password_reset')
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(password_reset_url, data)
        
        self.assertRedirects(response, reverse('password_reset_done'))
        # Even if no user exists, Django sends a success response to prevent email enumeration
        self.assertEqual(len(mail.outbox), 0)  # No email sent
    
    # ----------------------------
    # Profile View and Edit Tests
    # ----------------------------
    
    def test_profile_view_authenticated(self):
        """
        Test that an authenticated user can view their profile.
        """
        profile_url = reverse('ums:user_profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cms/user_profile.html')
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Test bio')
    
    def test_profile_view_unauthenticated(self):
        """
        Test that an unauthenticated user cannot view profiles.
        """
        self.client.credentials()  # Remove authentication by clearing credentials
        profile_url = reverse('ums:user_profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_profile_edit_authenticated(self):
        """
        Test that an authenticated user can edit their profile.
        """
        profile_edit_url = reverse('ums:user_profile_edit')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser_new@example.com'
        }
        response = self.client.post(profile_edit_url, data, follow=True)
        
        self.assertRedirects(response, reverse('ums:user_profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'testuser_new@example.com')
    
    def test_profile_edit_unauthenticated(self):
        """
        Test that an unauthenticated user cannot edit profiles.
        """
        self.client.credentials()  # Remove authentication by clearing credentials
        profile_edit_url = reverse('ums:user_profile_edit')
        data = {
            'first_name': 'Hacker',
            'last_name': 'Attack',
            'email': 'hacker@example.com'
        }
        response = self.client.post(profile_edit_url, data)
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    # ----------------------------
    # Role and Permission Management Tests
    # ----------------------------
    
    def test_role_management_admin_access(self):
        """
        Test that an admin user can manage roles.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        role_url = reverse('ums:role-list')
        data = {'name': 'Editor'}
        response = self.client.post(role_url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Role.objects.filter(name='Editor').count(), 1)
    
    def test_role_management_non_admin_access(self):
        """
        Test that a non-admin user cannot manage roles.
        """
        role_url = reverse('ums:role-list')
        data = {'name': 'Editor'}
        response = self.client.post(role_url, data, format='json')
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_permission_management_admin_access(self):
        """
        Test that an admin user can manage permissions.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        permission_url = reverse('ums:permission-list')
        data = {'name': 'can_edit'}
        response = self.client.post(permission_url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Permission.objects.filter(name='can_edit').count(), 1)
    
    def test_permission_management_non_admin_access(self):
        """
        Test that a non-admin user cannot manage permissions.
        """
        permission_url = reverse('ums:permission-list')
        data = {'name': 'can_edit'}
        response = self.client.post(permission_url, data, format='json')
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    # ----------------------------
    # User Management Tests
    # ----------------------------
    
    def test_user_management_admin_access(self):
        """
        Test that an admin can view and manage all users.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        user_list_url = reverse('ums:user-list')
        response = self.client.get(user_list_url, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), User.objects.count())
    
    def test_user_management_regular_user_access(self):
        """
        Test that a regular user can only view their own details.
        """
        user_detail_url = reverse('ums:user-detail', args=[self.user.id])
        response = self.client.get(user_detail_url, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        
        # Attempt to access another user's detail
        other_user_detail_url = reverse('ums:user-detail', args=[self.other_user.id])
        response = self.client.get(other_user_detail_url, format='json')
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    # ----------------------------
    # Token Refresh Tests
    # ----------------------------
    
    def test_token_refresh_success(self):
        """
        Test that a user can successfully refresh their access token.
        """
        refresh_url = reverse('ums:token_refresh')
        data = {'refresh': self.refresh_token}
        response = self.client.post(refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        
        # Update the access token cookie with the new access token
        new_access_token = response.data.get('access')
        self.assertIsNotNone(new_access_token, "New access token not found in response.")
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = new_access_token
    
    def test_token_refresh_invalid_token(self):
        """
        Test that token refresh fails with an invalid token.
        """
        refresh_url = reverse('ums:token_refresh')
        data = {'refresh': 'invalidtoken123'}
        response = self.client.post(refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)
    
    # ----------------------------
    # Token Lifetime View Test
    # ----------------------------
    
    def test_token_lifetime_view(self):
        """
        Test that the token_lifetime_view returns the correct access token lifetime.
        """
        token_lifetime_url = reverse('ums:token_lifetime')
        response = self.client.get(token_lifetime_url)
        
        self.assertEqual(response.status_code, 200)
        expected_lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=15)).total_seconds()
        self.assertEqual(response.json()['access_token_lifetime'], expected_lifetime)
    
    # ----------------------------
    # Additional Tests
    # ----------------------------
    
    def test_activate_account_expired_activation_id(self):
        """
        Test that activating with an expired activation ID fails.
        """
        # Simulate expired activation by deleting activation data
        registration_url = reverse('ums:register')
        data = {
            'username': 'expireduser',
            'email': 'expireduser@example.com',
            'password1': 'expiredpassword123',
            'password2': 'expiredpassword123',
        }
        response = self.client.post(registration_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        
        activation_id = cache.get('activation_email_expireduser@example.com')
        self.assertIsNotNone(activation_id)
        
        # Expire the activation data by deleting it from cache
        cache.delete(f'activation_{activation_id}')
        cache.delete('activation_email_expireduser@example.com')
        
        activate_url = reverse('ums:activate', kwargs={'activation_id': activation_id})
        response = self.client.get(activate_url)
        
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'registration/activation_invalid.html')
    
    def test_password_reset_flow(self):
        """
        Test the complete password reset flow.
        """
        # Initiate password reset
        password_reset_url = reverse('password_reset')
        data = {'email': 'testuser@example.com'}
        response = self.client.post(password_reset_url, data)
        self.assertRedirects(response, reverse('password_reset_done'))
        
        # Check that a password reset email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset Requested', mail.outbox[0].subject)
        
        # Extract uid and token from email
        # Assuming the email contains a link like /password-reset-confirm/<uid>/<token>/
        # For simplicity, simulate generating uid and token
        user = User.objects.get(email='testuser@example.com')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        password_reset_confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        
        # Complete password reset
        new_password = 'newsecurepassword123'
        reset_data = {
            'new_password1': new_password,
            'new_password2': new_password,
        }
        response = self.client.post(password_reset_confirm_url, reset_data, format='json')
        self.assertRedirects(response, reverse('password_reset_complete'))
        
        # Verify that the user's password has been updated
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))
    
    # ----------------------------
    # Role and Permission Assignment Tests
    # ----------------------------
    
    def test_assign_role_to_user_admin(self):
        """
        Test that an admin can assign a role to a user.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        assign_role_url = reverse('ums:user-detail', args=[self.other_user.id])
        data = {
            'role': self.role_admin.id
        }
        response = self.client.patch(assign_role_url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.role, self.role_admin)
    
    def test_assign_role_to_user_non_admin(self):
        """
        Test that a non-admin user cannot assign roles to other users.
        """
        assign_role_url = reverse('ums:user-detail', args=[self.other_user.id])
        data = {
            'role': self.role_admin.id
        }
        response = self.client.patch(assign_role_url, data, format='json')
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_permission_assignment_admin(self):
        """
        Test that an admin can assign permissions to roles.
        """
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        assign_permission_url = reverse('ums:permission-list')
        data = {'name': 'can_delete'}
        response = self.client.post(assign_permission_url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Permission.objects.filter(name='can_delete').count(), 1)
        
        # Assign permission to role_admin
        permission = Permission.objects.get(name='can_delete')
        self.role_admin.permissions.add(permission)
        self.assertTrue(self.role_admin.permissions.filter(name='can_delete').exists())
    
    def test_permission_assignment_non_admin(self):
        """
        Test that a non-admin user cannot assign permissions to roles.
        """
        permission_url = reverse('ums:permission-list')
        data = {'name': 'can_delete'}
        response = self.client.post(permission_url, data, format='json')
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    # ----------------------------
    # Enrollment and Progress Tests
    # ----------------------------
    
    def test_enrollment_creation(self):
        """
        Test that a user can be enrolled in a course.
        """
        enrollment_url = reverse('cms:enrollment-list')  # Ensure this matches your cms/urls.py
        data = {
            'user': self.other_user.id,
            'course': self.course.id
        }
        response = self.client.post(enrollment_url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Enrollment.objects.filter(user=self.other_user, course=self.course).exists())
    
    def test_user_progress_update(self):
        """
        Test that a user's progress can be updated.
        """
        progress_url = reverse('cms:userprogress-list')  # Ensure this matches your cms/urls.py
        data = {
            'user': self.user.id,
            'course': self.course.id,
            'progress': 75  # Assuming progress is a percentage
        }
        response = self.client.post(progress_url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        progress = UserProgress.objects.get(user=self.user, course=self.course)
        self.assertEqual(progress.progress, 75)
    
    # ----------------------------
    # Cleanup After Tests
    # ----------------------------
    
    def tearDown(self):
        """
        Clean up after each test method.
        """
        self.client.credentials()  # Remove authentication by clearing credentials
        cache.clear()  # Clear cache to prevent interference between tests
