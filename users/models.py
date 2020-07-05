import jwt
from datetime import datetime, timedelta
from django.conf import settings

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import MyUserManager
from django.utils import timezone
import random, string, calendar

import os


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True)
    username = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MyUserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            'exp': calendar.timegm(dt.timetuple()),
            'email': self.email
        }, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')

    def safe_get(id=None):
        try:
            a_key = User.objects.get(id=id)
            return a_key
        except User.DoesNotExist:
            return None


class UserProfile(models.Model):
    avatar = models.ImageField(upload_to='users_avatars', default=os.path.join('users_avatars', 'default.png'))
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    birth_date = models.DateTimeField(default=timezone.datetime(year=2000, month=1, day=1))
    interests = models.TextField(default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    is_private = models.BooleanField(default=False)
    available_to = models.ManyToManyField(User, related_name='available_profiles')
    followers = models.ManyToManyField(User, related_name='subscriptions')

    @staticmethod
    def safe_filter( user: User):
        try:
            return UserProfile.objects.filter(user=user)
        except UserProfile.DoesNotExist:
            return None


class AuthKey(models.Model):
    key = models.CharField(max_length=50, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def safe_get(key=None):
        try:
            a_key = AuthKey.objects.get(key=key)
            return a_key
        except AuthKey.DoesNotExist:
            return None

    @staticmethod
    def gen_key(n):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(n))


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True)
    text = models.TextField(default='')
    receiving_time = models.DateTimeField(default=timezone.datetime.now())
    is_request = models.BooleanField(default=True)
