from django.test import TestCase
from .models import User, Role, Permission, Profile

class PermissionModelTest(TestCase):
    def test_permission_creation(self):
        permission = Permission.objects.create(name="Edit Content", description="Can edit content")
        self.assertEqual(permission.name, "Edit Content")
        self.assertEqual(permission.description, "Can edit content")
        self.assertEqual(str(permission), "Edit Content")


class RoleModelTest(TestCase):
    def setUp(self):
        self.permission1 = Permission.objects.create(name="Edit Content")
        self.permission2 = Permission.objects.create(name="Delete Content")

    def test_role_creation(self):
        role = Role.objects.create(name="Editor", description="Can edit and delete content")
        role.permissions.add(self.permission1, self.permission2)
        
        self.assertEqual(role.name, "Editor")
        self.assertEqual(role.description, "Can edit and delete content")
        self.assertIn(self.permission1, role.permissions.all())
        self.assertIn(self.permission2, role.permissions.all())
        self.assertEqual(str(role), "Editor")


class UserModelTest(TestCase):
    def setUp(self):
        # Create Role and Permission objects for the user
        self.permission = Permission.objects.create(name="View Content")
        self.role = Role.objects.create(name="Viewer", description="Can only view content")
        self.role.permissions.add(self.permission)

    def test_user_creation(self):
        # Create a User with associated role
        user = User.objects.create_user(username="johndoe", email="johndoe@example.com", password="password123")
        user.role = self.role
        user.save()

        self.assertEqual(user.username, "johndoe")
        self.assertEqual(user.email, "johndoe@example.com")
        self.assertEqual(user.role, self.role)
        self.assertIn(self.permission, user.role.permissions.all())
        self.assertEqual(user.total_points, 0)
        self.assertEqual(user.level, 1)
        self.assertEqual(str(user), "johndoe")

    def test_profile_creation_on_user_creation(self):
        # Check if Profile is automatically created when a User is created
        user = User.objects.create_user(username="janedoe", email="janedoe@example.com", password="password123")
        
        # Verify that the Profile is created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(str(user.profile), "janedoe's Profile")


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="janesmith", email="janesmith@example.com", password="password123")

    def test_profile_fields(self):
        # Access the automatically created Profile
        profile = self.user.profile
        profile.bio = "Software Engineer with 5 years of experience"
        profile.save()

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, "Software Engineer with 5 years of experience")
        self.assertEqual(str(profile), "janesmith's Profile")

    def test_profile_update_on_user_update(self):
        # Test if Profile remains consistent when User is updated
        self.user.username = "updatedname"
        self.user.save()
        
        # Fetch the profile after update
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.user.username, "updatedname")
        self.assertEqual(str(profile), "updatedname's Profile")
