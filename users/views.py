from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.reverse import reverse
from django.core.mail import send_mail
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser
from users.serializers import *
from users.models import *


# Create your views here.

class SignUpView(APIView):
    def post(self, request):
        sign_up = SignUpSerializer(data=request.data)
        sign_up.is_valid(True)
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
            user.is_active = True
            user.save()
            auth_key.delete()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'Activation error': 'no such registered authentication key'},
                            status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, created = Token.objects.get_or_create(user_id=serializer.user_id)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response(status=status.HTTP_200_OK)


class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, user_id=None):
        if not user_id and not request.user.is_authenticated:
            return Response({'errors': ['user profile does not exist']}, status=status.HTTP_404_NOT_FOUND)
        elif not user_id and request.user.is_authenticated:
            serializer = UserProfileSerializer(UserProfile.objects.get(user=request.user))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            buttons = []
            profile_form = None
            if UserProfile.objects.filter(user=User.safe_get(id=user_id)):
                profile_form = UserProfile.objects.get(user=User.objects.get(id=user_id))
            else:
                buttons.append({
                    'url': request.build_absolute_uri(reverse('users_app:profile_create')),
                    'name': 'Create'
                })
                return Response({
                    'message': 'user profile does not exist',
                    'buttons': 'Create'
                }, status=status.HTTP_404_NOT_FOUND)
            if request.user.id == user_id \
                    or not profile_form.is_private \
                    or (request.user.is_authenticated and profile_form in request.user.available_profiles.all()):
                serializer = UserProfileSerializer(profile_form)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                if request.user.is_authenticated:
                    buttons.append({
                        'url': request.build_absolute_uri(reverse('users_app:perm_req', args=[user_id])),
                        'name': 'Попросить разрешения'
                    })
                return Response({
                    'message': 'you don\'t have permission to open this profile'
                }, status=status.HTTP_403_FORBIDDEN)


class ProfileCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        profile = UserProfile(user=User.objects.get(id=request.user.id))
        profile.save()
        return Response(status=status.HTTP_201_CREATED)


class EditProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser]

    def get(self, request):
        profile = UserProfileSerializer(UserProfile.objects.get(user=request.user))
        return Response(profile.data)

    def post(self, request):
        old_avatar_path = os.path.join(settings.MEDIA_ROOT,
                                       str(UserProfile.objects.get(user=request.user).avatar.name))
        serializer = UserProfileSerializer(data=request.data, instance=UserProfile.objects.get(user=request.user))
        serializer.is_valid(True)
        if 'avatar' in request.FILES:
            if os.path.basename(old_avatar_path) != 'default.png':
                try:
                    os.remove(old_avatar_path)
                except:
                    return Response({'error': 'can\'t delete old avatar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer.save()
        return Response(status=status.HTTP_200_OK)


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # subscribe
    def get(self, request, user_id):
        profile = UserProfile.objects.get(user_id=user_id)
        if (not profile.is_private) or request.user in profile.available_to.all():
            subs = User.objects.get(id=request.user.id).subscriptions
            if not profile in subs.all() and user_id != request.user.id:
                subs.add(profile)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'message': 'impossible to subscribe private profile'}, status=status.HTTP_403_FORBIDDEN)

    # unsubscribe
    def delete(self, request, user_id):
        profile = UserProfile.objects.get(user_id=user_id)
        if request.user in profile.followers.all():
            User.objects.get(id=request.user.id).subscriptions.remove(profile)
        return Response(status=status.HTTP_200_OK)


class SubscriptionsListView(generics.ListAPIView):
    serializer_class = UserInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return [User.objects.get(userprofile=profile) for profile in self.request.user.subscriptions.all()]


class FollowersListView(generics.ListAPIView):
    serializer_class = UserInfoSerializer
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
        return UserProfile.objects.get(user=user).followers.all()


class PermissionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, user_id: int):
        user = User.objects.get(id=user_id)
        notification = Notification(
            sender=request.user,
            receiver=user,
            text='user ' + request.user.username + ' requests permission to access your profile'
        )
        if not Notification.objects.filter(receiving_time=notification.receiving_time,
                                           sender=request.user).exists():
            notification.save()
            user.notifications.add(notification)
            return Response({'message': 'your message sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class PermissionAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, user_id=None):
        user = User.objects.get(id=request.user.id)
        sender = User.objects.get(id=user_id)

        sender.available_profiles.add(UserProfile.objects.get(user=user))
        user.save()
        Notification.objects.filter(sender=sender, is_request=True).delete()
        return Response(status=status.HTTP_200_OK)


class NotificationsListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)


class NotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def delete(self, request, notification_id: int):
        notification = None
        try:
            notification = Notification.objects.get(id=notification_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if notification.receiver.id == request.user.id:
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
