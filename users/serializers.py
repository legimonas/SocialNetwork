from abc import ABC

import os

from PIL import Image
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    avatar = serializers.FileField(write_only=True)

    class Meta:
        model = UserProfile
        exclude = ['available_to']

    def get_followers(self, instance):
        followers = []
        for follower in instance.followers.all():
            followers.append({
                'username': follower.username,
                'id': follower.pk
            })
        return followers

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        default = False

        if not 'avatar' in validated_data:
            default = True

        name, extension = os.path.splitext(validated_data['avatar'].name)

        if default:
            instance.avatar.name = os.path.join('users_avatars', 'default.jpg')
            instance.save()
            return instance

        instance.avatar.name = name + '__' + str(instance.id) + extension
        validated_data['avatar'].name = instance.avatar.name
        instance.save()
        image = None
        if os.path.basename(instance.avatar.name) == 'default.jpg':
            image = Image.open(os.path.join(settings.MEDIA_ROOT, 'users_avatars', 'default.jpg'))
        else:
            image = Image.open(os.path.join(settings.MEDIA_ROOT, 'users_avatars', instance.avatar.name))
            # image = Image.open(validated_data['avatar'])

        image.thumbnail((200, 200))
        # image.save(os.path.join(settings.MEDIA_ROOT, 'users_avatars', instance.avatar.name))

        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)

        return instance


class SignUpSerializer(serializers.ModelSerializer):
    pass2 = serializers.CharField(max_length=50, required=True, write_only=True)

    def validate(self, attrs):
        if not ('@' in attrs['email']):
            raise serializers.ValidationError({'email': 'bad format for mail'})
        if not attrs['pass2'] == attrs['password']:
            raise serializers.ValidationError({'password': 'passwords don\'t match'})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'this email has already exist'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'], username=validated_data['username'])
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'pass2', 'password']


class LoginSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']

        if email is None:
            raise serializers.ValidationError('An email address is required to log in.')

        if password is None:
            raise serializers.ValidationError('A password is required to log in.')

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError('A user with this email and password was not found.')

        if not user.is_active:
            raise serializers.ValidationError('This user has been deactivated.')
        self.user_id = user.pk
        return attrs

    class Meta:
        model = User
        fields = ['email', 'password', 'user_id']
        extra_kwargs = {
            'email': {
                'validators': [UnicodeUsernameValidator()],
            }
        }