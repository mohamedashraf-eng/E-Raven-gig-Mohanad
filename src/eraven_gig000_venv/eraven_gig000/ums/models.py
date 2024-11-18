from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product

class Permission(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Permission Name")
    description = models.TextField(blank=True, null=True, verbose_name="Permission Description")

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Role Name")
    description = models.TextField(blank=True, null=True, verbose_name="Role Description")
    permissions = models.ManyToManyField(
        Permission, related_name='roles', blank=True, verbose_name="Role Permissions"
    )

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    # LMS-specific fields
    total_points = models.PositiveIntegerField(default=0)  # Accumulated points from all activities
    level = models.PositiveIntegerField(default=1)  # Level based on points or achievements

    # Additional optional fields
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Relationship with bundles/products
    bundles = models.ManyToManyField(
        Product, related_name='users', blank=True, verbose_name="Purchased Products"
    )

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_access_to_course(self, course):
        """
        Check if the user has access to a course through purchased products.
        """
        return self.bundles.filter(courses=course).exists()


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', verbose_name="User Profile"
    )
    bio = models.TextField(blank=True, null=True, verbose_name="Bio")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Profile of {self.user.username}"


# Signal to create or update a Profile automatically when a User is created or updated.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Update the existing profile if it exists.
        if hasattr(instance, 'profile'):
            instance.profile.save()
