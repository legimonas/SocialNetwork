import operator
from copy import copy

from django.db.models import QuerySet
from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .serializers import *
from users.serializers import UserInfoSerializer

# Create your views here.


class PostView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser]

    def post(self, request):
        data = copy(request.data)
        post_serializer = PostCreateSerializer(data=request.data)
        post_serializer.is_valid(True)
        post_serializer.validated_data['creator'] = request.user
        post = post_serializer.save()

        return Response(status=status.HTTP_201_CREATED)

    def get(self, request, post_id:int):
        post = Post.objects.get(id=post_id)
        serializer = PostGetSerializer(post)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        likes = post.likes
        if request.user in likes.all():
            likes.remove(request.user)
        else:
            likes.add(request.user)
        return Response(status=status.HTTP_200_OK)


class PostFunsListView(generics.ListAPIView):
    serializer_class = UserInfoSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Post.objects.get(id=self.kwargs['post_id']).likes


class RecommendationsListView(generics.ListAPIView):
    serializer_class = PostGetSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        recommendations = Post.objects.none()
        for profile in self.request.user.subscriptions.all():
            recommendations = recommendations | Post.objects.filter(creator=User.objects.get(id=profile.user_id)).all()
        return recommendations.distinct().order_by('-publication_date')


class PostsListByUserView(generics.ListAPIView):
    serializer_class = PostGetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = None
        if 'user_id' in self.kwargs:
            user = User.objects.get(id=self.kwargs['user_id'])
        if not user:
            user = self.request.user
        if not user:
            raise ValidationError('user not specified')
        return Post.objects.filter(creator=user).distinct().order_by('-publication_date')
