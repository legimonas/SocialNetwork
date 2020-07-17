import os
from typing import Any

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from rest_framework import status
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from PIL import Image
from io import BytesIO
from users.tests import UserAuthClass

from .models import *


class PostsTests(UserAuthClass):
    token1 = str()
    token2 = str()

    @staticmethod
    def get_test_file(filename: str):
        file = File(open(os.path.join(settings.MEDIA_DIR, 'tests', filename), 'rb'))
        return InMemoryUploadedFile(file, None, filename, os.path.splitext(filename)[-1][1:], file.tell(), None)

    def setUp(self):
        self.token1 = self.create_and_activate_account('example@gmail.com', '12345', '12345', 'ExampleName')
        self.token2 = self.create_and_activate_account('user@gmail.com', 'qwerty', 'qwerty', 'UserName')

    def delete_files(self, files: list):
        for filename in files:
            os.remove(os.path.join(settings.MEDIA_DIR, 'posts_attachments', filename))

    def post_create(self, auth_token: str, title: str, text: str, attach: bool):
        attachs = []
        if attach:
            attachs = [
                self.get_test_file('test.jpg'),
                self.get_test_file('test.mp3'),
                self.get_test_file('test.mp4'),
            ]
        data = {
            'title': title,
            'text': text,
            'attachments': attachs,
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + auth_token)
        url = reverse('posts_app:create')
        posts_count = Post.objects.count()
        attachs_count = Attach.objects.count()
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), posts_count + 1)

        if attach:
            self.assertEqual(Attach.objects.count(), attachs_count + 3)
        return response

    def test_post_create_and_get(self):
        # создаем запись с файлами различного расширения
        response = self.post_create(self.token1, 'title1', 'text1', True)

        # пытаемся получить данные этой записи
        url = reverse('posts_app:get', args=[Post.objects.get().id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'title1')
        self.assertEqual(len(response.data['attachments']), 3)
        self.delete_files(['test.jpg', 'test.mp3', 'test.mp4'])

    def test_likes_and_funs(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
        self.post_create(self.token1, 'title', 'text1', False)
        post = Post.objects.get()

        # пробуем "лайкнуть" пост
        url = reverse('posts_app:like', args=[post.id])
        self.client.get(url)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.likes.count(), 2)

        # получаем список пользователей, "лайкнувших" данный пост
        url = reverse('posts_app:funs', args=[post.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # пробуем "снять лайк"
        url = reverse('posts_app:like', args=[post.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.likes.count(), 1)

    def test_recommendations_and_user_posts_list(self):
        # создаем дополнительного пользователя и несколько записей
        token3 = self.create_and_activate_account('user3@gmail.com', '11111', '11111', 'somebody')

        id1 = User.objects.get(id=Token.objects.get(key=self.token1).user_id).id
        id2 = User.objects.get(id=Token.objects.get(key=self.token2).user_id).id

        self.post_create(self.token1, 'user1title1', 'text1', False)
        self.post_create(self.token1, 'user1title2', 'text2', False)
        self.post_create(self.token2, 'user2title1', 'text1', False)
        self.post_create(token3, 'user3title1', 'text1', False)

        # запись оказывается в рекомендациях, если оформлена подписка на создателя этой записи - подписываемся
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token3)
        url = reverse('users_app:subscribe', args=[id1])
        self.client.get(url)

        # получаем рекомендации и проверяем, чтобы они были отсортированы по дате
        # и создателем был пользователь, на которого оформлена подписка
        url = reverse('posts_app:recommendations')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['creator']['username'], 'ExampleName')
        self.assertEqual(response.data[1]['creator']['username'], 'ExampleName')
        self.assertTrue(response.data[0]['publication_date'] > response.data[1]['publication_date'])

        right_data = response.data

        # проверяем получение личных записей по токену авторизации
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
        url = reverse('posts_app:user_articles')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(right_data, response.data)

        # проверяем получение личных записей по id пользователя
        url = reverse('posts_app:user_articles', args=[id2])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'user2title1')

