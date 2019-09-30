from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import MyUserManager
from django.utils import timezone

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True)
    username = models.CharField(max_length=50)
    birth_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MyUserManager()
    def __str__(self):
        return self.email




class UserProfile(models.Model):
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    birth_date = models.DateTimeField()
    interests = models.TextField(default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)


class AuthKey(models.Model):
    key = models.CharField(max_length=50, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def safe_get(key=None):
        try:
            akey = AuthKey.objects.get(key=key)
            return akey
        except AuthKey.DoesNotExist:
            return None