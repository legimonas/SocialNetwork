from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm
from . import models


class MyUserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        profile = models.UserProfile(user=user)
        profile.save()
        return user

    def create_user(self, form: ModelForm):
        user = form.save()
        profile = models.UserProfile(user=user)
        profile.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

    def safe_get(self, email=None, username=None, password=None):
        try:
            user = self.get(email=email, password=password, username=username)
            return user
        except self.model.DoesNotExist:
            return None
