from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from PIL import Image
from io import BytesIO

from users.models import *

# Create your tests here.

class UserAuthClass(APITestCase):

    def create_and_activate_account(self, email:str, password:str, pass2:str, username:str):
        url = reverse('users_app:signup')
        users_count = User.objects.count()
        authkeys_count = AuthKey.objects.count()
        profiles_count = UserProfile.objects.count()
        data = {
            'email': email,
            'password': password,
            'pass2': pass2,
            'username': username,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'message': 'please, confirm your mail address'})
        self.assertEqual(User.objects.count(), users_count+1)
        User.objects.get(email=email)
        self.assertEqual(AuthKey.objects.count(), authkeys_count+1)
        self.assertEqual(UserProfile.objects.count(), profiles_count+1)

        url = reverse('users_app:activate', kwargs={'key': AuthKey.objects.get().key})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(id=Token.objects.get(key=response.data['token']).user_id).is_active)
        self.assertEqual(AuthKey.objects.count(), authkeys_count)
        self.assertTrue('token' in response.data)
        return response.data['token']

    def logout(self, token: str):
        auth_tokens_count = Token.objects.count()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        url = reverse('users_app:logout')
        response = self.client.get(url)
        self.client.credentials()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), auth_tokens_count-1)
        with self.assertRaises(ObjectDoesNotExist) as context:
            Token.objects.get(key=token)

    def login(self, email: str, password: str):
        auth_tokens_count = Token.objects.count()

        data = {
            'email': email,
            'password': password,
        }
        url = reverse('users_app:login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), auth_tokens_count+1)
        self.assertTrue('token' in response.data)
        return response.data['token']


class UsersTests(UserAuthClass):
    token1 = str()
    token2 = str()

    def generate_photo_file(self, name:str):
        file = BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = name + '.png'
        file.seek(0)
        return file

    def setUp(self):
        self.token1 = self.create_and_activate_account('example1@gmail.com', '12345', '12345', 'NoName1')
        self.token2 = self.create_and_activate_account('example2@gmail.com', '11111', '11111', 'NoName2')

    def test_login_and_logout(self):
        self.logout(self.token1)
        self.token1 = self.login(email='example1@gmail.com', password='12345')

    def test_profile_editing(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
        url = reverse('users_app:edit_profile')
        data = {
            'first_name': 'FirstName',
            'last_name': 'LastName',
            'is_private': True,
            'avatar': self.generate_photo_file('photo'),
            'interests': 'some interests'
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('users_app:profile'))
        rdata = response.data
        for key in data:
            if key != 'avatar':
                self.assertEqual(data[key], rdata[key])
        print(rdata['avatar'])

        old_avatar_path = os.path.join(settings.BASE_DIR, 'media', 'users_avatars', os.path.basename(rdata['avatar']))

        if os.path.basename(old_avatar_path) != 'default.png':
            os.remove(old_avatar_path)

        self.client.credentials()

    def test_profile_privacy(self):
        id1 = User.objects.get(id=Token.objects.get(key=self.token1).user_id).id
        id2 = User.objects.get(id=Token.objects.get(key=self.token2).user_id).id

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)

        # делаем один из профелей приватным
        url = reverse('users_app:edit_profile')
        data = {
            'is_private': True,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # пытаемся получить данные приватного профиля с аккаунта, которому не открыт доступ
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2)
        url = reverse('users_app:profile', kwargs={'user_id': id1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'message': "you don't have permission to open this profile"})

        # просим разрешения на доступ
        url = reverse('users_app:perm_req', kwargs={'user_id': id1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'your message sent successfully'})
        self.assertEqual(Notification.objects.count(), 1)

        # одобряем доступ
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
        url = reverse('users_app:perm_acc', kwargs={'user_id': id2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(UserProfile.objects.get(user_id=User.objects.get(id=id1).id).available_to.count(), 1)

        # пытаемся снова получить данные профиля
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2)
        url = reverse('users_app:profile', kwargs={'user_id': id1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('first_name' in response.data)

    def test_subscriptions(self):
        id2 = User.objects.get(id=Token.objects.get(key=self.token2).user_id).id

        # проверяем возможность подписки
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
        url = reverse('users_app:subscribe', args=[id2])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfile.objects.get(user_id=id2).followers.count(), 1)

        # проверяем "списочные" контроллеры
        # 1) Список подписок
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
        url = reverse('users_app:subscriptions')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'NoName2')

        # 2) список подписчиков с указанием id пользователя
        url = reverse('users_app:followers', args=[id2])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'NoName1')
        data1 = response.data

        # 3) список подписчиков с указание токена авторизации
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2)
        url = reverse('users_app:followers')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data1)

        # проверка возможности отписки
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
        url = reverse('users_app:subscribe', args=[id2])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfile.objects.get(user_id=id2).followers.count(), 0)

        # проверка запрета подписки на приватный профиль
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2)
        url = reverse('users_app:edit_profile')
        data = {
            'is_private': True,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
        url = reverse('users_app:subscribe', args=[id2])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserProfile.objects.get(user_id=id2).followers.count(), 0)
