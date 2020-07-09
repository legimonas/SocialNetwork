from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from users.models import User, AuthKey, UserProfile

# Create your tests here.

class RegisterUserClass(APITestCase):
    def create_and_activate_account(self):
        url = reverse('users_app:signup')
        data = {
            'email': 'example@gmail.com',
            'password': '12345',
            'pass2': '12345',
            'username': 'NoName',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'message': 'please, confirm your mail address'})
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'example@gmail.com')
        self.assertEqual(AuthKey.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)

        url = reverse('users_app:activate', kwargs={'key': AuthKey.objects.get().key})
        self.assertFalse(User.objects.get().is_active)


class UsersTests(RegisterUserClass):
    def test_create_and_activate_account(self):
        self.create_and_activate_account()
    

