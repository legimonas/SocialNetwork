from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import MyUserManager
from django.utils import timezone
import random, string


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True)
    username = models.CharField(max_length=50)
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
    birth_date = models.DateTimeField(default=timezone.datetime(year=2000, month=1, day=1))
    interests = models.TextField(default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    @staticmethod
    def get_profile_from_form(**kwargs):
        return UserProfile(first_name=kwargs.get('first_name'),
                           last_name=kwargs.get('last_name'),
                           birth_date=kwargs.get('birth_date'),
                           interests=kwargs.get('interests'))

    def set_profile_from_form(self, **kwargs):
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.birth_date = kwargs.get('birth_date')
        self.interests = kwargs.get('interests')


class AuthKey(models.Model):
    key = models.CharField(max_length=50, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def safe_get(key=None):
        try:
            akey = AuthKey.objects.get(key=key)
            return akey
        except AuthKey.DoesNotExist:
            return None

    @staticmethod
    def gen_key(n):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(n))
