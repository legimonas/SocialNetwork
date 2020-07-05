from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import *


# Create your views here.

class SignUpView(APIView):
    def post(self, request):
        sign_up = SignUpSerializer(data=request.data)
        if sign_up.is_valid(False):
            sign_up.save()
        return Response(
            {
                'token': sign_up.data.get('token', None),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, user_id=None):
        if not user_id and not request.user.is_authenticated:
            return Response({'errors': ['user profile is not existing']}, status=status.HTTP_404_NOT_FOUND)
        elif not user_id and request.user.is_authenticated:
            serializer = UserProfileSerializer(UserProfile.objects.get(user=request.user))
            return Response(serializer.data)
        else:
            buttons = []
            profile_form = None
            if UserProfile.safe_filter(user=User.safe_get(id=user_id)):
                profile_form = UserProfile.objects.get(user=User.objects.get(id=user_id))
            else:
                # доделать!!!!
                buttons.append({
                    #     'url': request.build_absolute_uri(reverse('users_app:profile_create')),
                    'name': 'Создать'
                })
                return Response({
                    'message': 'user profile is not existing',
                    'buttons': 'Create'
                }, status=status.HTTP_404_NOT_FOUND)
            if request.user.id == user_id \
                    or not profile_form.is_private \
                    or (request.user.is_authenticated and profile_form in request.user.available_profiles.all()):
                serializer = UserProfileSerializer(profile_form)
                return Response(serializer.data)
            else:
                if request.user.is_authenticated:
                    # доделать!!!!
                    buttons.append({
                        # 'url': request.build_absolute_uri(reverse('users_app:perm_req', args=[user_id])),
                        'name': 'Попросить разрешения'
                    })
                return Response({
                    'message': 'you don\'t have permission to open this profile'
                }, status=status.HTTP_403_FORBIDDEN)


