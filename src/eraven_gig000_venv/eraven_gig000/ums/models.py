# ums/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Extend the default user model
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('instructor', 'Instructor'), ('student', 'Student')])

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

class Permission(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

class Role(models.Model):
    name = models.CharField(max_length=10, unique=True)
    permissions = models.ManyToManyField(Permission)
