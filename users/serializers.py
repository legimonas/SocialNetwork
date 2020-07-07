from abc import ABC

from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth import authenticate, login, logout

from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        exclude = ['available_to', 'is_private']

    def get_followers(self, instance):
        followers = []
        for follower in instance.followers.all():
            followers.append({
                'username': follower.username,
                'id': follower.pk
            })
        return followers

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