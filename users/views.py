from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from django.core.mail import send_mail
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import *
from .models import *


# Create your views here.

class SignUpView(APIView):
    def post(self, request):
        sign_up = SignUpSerializer(data=request.data)
        sign_up.is_valid(False)
        user = sign_up.save()
        auth_key = AuthKey(key=AuthKey.gen_key(10), user=user)
        auth_key.save()
        auth_ref = request.build_absolute_uri(reverse('users_app:activate', args=[auth_key.key]))
        email = send_mail('Hello!!!',
                          'Please, confirm your registration:\n' + auth_ref,
                          'progr.0820@mail.ru',
                          [user.email],
                          fail_silently=True)
        return Response(
            {
                'message': 'please, confirm your mail address',
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateView(APIView):
    def get(self, request, key):
        auth_key = AuthKey.safe_get(key=key)
        if auth_key is not None:
            user = auth_key.user
            print(user)
            user.is_active = True
            user.save()
            auth_key.delete()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'Activation error': 'no such registered authentication key'}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, created = Token.objects.get_or_create(user_id=serializer.user_id)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        auth = get_authorization_header(request).split()
        token = Token.objects.get(key=auth[1].decode())
        token.delete()
        return Response(status=status.HTTP_200_OK)

class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, user_id=None):
        user_profile = UserProfile()
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


