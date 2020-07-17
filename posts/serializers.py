from __future__ import unicode_literals

import os
from rest_framework import serializers
from django.conf import settings
from users.models import User, UserProfile
from users.serializers import UserInfoSerializer
from .models import *


class PostCreateSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(child=serializers.FileField(), allow_empty=True, required=False)

    def create(self, validated_data):
        post = Post(creator=validated_data['creator'], title=validated_data['title'], text=validated_data['text'])
        post.save()
        if 'attachments' in validated_data:
            for file in validated_data['attachments']:
                ext = os.path.splitext(file.name)[-1][1:]
                attach = Attach(file=file, file_extension=ext, post=post)
                attach.save()
        return post

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'attachments',
            'creator',
        ]


class AttachSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attach
        fields = [
            'file',
            'file_extension',
        ]


class PostGetSerializer(serializers.ModelSerializer):
    likes = UserInfoSerializer(many=True, read_only=True)
    creator = UserInfoSerializer(many=False, read_only=True)
    attachments = serializers.SerializerMethodField()

    def get_attachments(self, instance):
        return AttachSerializer(Attach.objects.filter(post_id=instance.id).all(), many=True).data

    class Meta:
        model = Post
        fields = '__all__'


class PostLikesSerializer(serializers.ModelSerializer):
    likes = UserInfoSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    def get_likes_count(self, instance):
        return instance.likes.count()

    class Meta:
        model = Post
        fields = [
            'likes',
            'likes_count'
        ]