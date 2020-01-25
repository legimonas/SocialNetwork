from django.shortcuts import render, redirect, render_to_response
from django.core.mail import send_mail
from django.views import View
from django.urls import reverse
from .forms import *
from users.models import *
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import os


class SignUp(View):
    def get(self, request):
        return render(request, 'users/signup.html')

    def post(self, request):
        form = UserForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(form)

            auth_key = AuthKey(key=AuthKey.gen_key(10), user=user)
            auth_key.save()
            auth_ref = request.build_absolute_uri(reverse('users_app:activate', args=[auth_key.key]))
            email = send_mail('Hello!!!',
                              'Please, confirm your registration:\n' + auth_ref,
                              'progr.0820@mail.ru',
                              [user.email],
                              fail_silently=True)

            return render(request, 'users/Message.html',
                          context={
                              'message': 'На ваш почтовый адрес было отправлено письмо с подтверждением аккаунта!!!'})
        else:
            f = {}
            for key in request.POST:
                f[key] = request.POST.get(key)
            f.pop('csrfmiddlewaretoken')

            return render(request, 'users/signup.html', context={'errors': form.errors.as_data(), 'form': f})

        # return render(request, 'users/edit_profile.html', context={'errors': errors, 'form': form})


class Login(View):
    def get(self, request):

        return render(request, 'users/login.html')

    def post(self, request):
        form_from_request = LoginForm(request.POST)
        form = {}

        if form_from_request.is_valid():
            form = form_from_request.cleaned_data
        else:
            return render(request, 'users/login.html', context={'login_error': form_from_request.errors})

        user = authenticate(email=form['email'],
                            password=form['password'])

        if user is not None:
            login(request, user)
            return redirect('home_app:home')
        else:
            return render(request, 'users/login.html', context={'login_error': 'Неверная почта или пароль'})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('home_app:home')


class Activate(View):
    def get(self, request, key):
        auth_key = AuthKey.safe_get(key=key)
        if auth_key is not None:
            user = auth_key.user
            print(user)
            user.is_active = True
            user.save()
            auth_key.delete()
        return redirect('users_app:login')


class ProfileView(View):
    def get(self, request, user_id=None):
        if not user_id:
            return redirect('home_app:home')
        else:
            profile_form = UserProfile.objects.get(user=User.objects.get(id=user_id))
            if request.user.id == user_id \
                    or not profile_form.is_private \
                    or profile_form in request.user.available_profiles.all():
                return render(request, 'users/profile.html', context={'profile_form': profile_form})
            else:
                buttons = []
                if request.user.is_authenticated:
                    buttons.append({
                        'url': request.build_absolute_uri(reverse('users_app:perm_req', args=[user_id])),
                        'name': 'Попросить разрешения'
                    })
                return render(request, 'users/Message.html', context={
                    'message': 'У вас нет доступа к этому профилю',
                    'buttons': buttons
                })


class EditProfileView(View):

    def get(self, request, user_id=None):
        if not user_id:
            return redirect('home_app:home')
        else:
            profile_form = UserProfile.objects.get(user=User.objects.get(id=user_id))
            if profile_form:
                return render(request, 'users/edit_profile.html', context={'profile_form': profile_form})
            else:
                return render(request, 'home_app/homepage.html')

    def post(self, request, user_id=None):
        form = UserProfileForm(request.POST, request.FILES, instance=UserProfile.objects.get(user=request.user))
        if form.is_valid():
            old_avatar_path = os.path.join(settings.MEDIA_ROOT,
                                           str(UserProfile.objects.get(user=request.user).avatar.name))

            if 'avatar' in request.FILES:
                print('t')
                try:
                    os.remove(old_avatar_path)
                except:
                    print('can not delete old image')
                form.save(filename=request.FILES['avatar'].name)
            else:
                form.save()

            return redirect('users_app:profile', user_id)
        else:
            return render(request, 'users/edit_profile.html', context={'message': form.errors})


class NotificationsView(View):
    def get(self, request, user_id=None):
        if not user_id:
            return redirect('home_app:home')
        else:
            notifications = Notification.objects.filter(receiver=User.objects.get(id=user_id))

            return render(request, 'users/Notifications.html', context={'notifications': notifications})


class PermissionDisable(View):
    def get(self, request, notification_id=None):
        if notification_id:
            Notification.objects.filter(id=notification_id).delete()

        return redirect('users_app:notifications', request.user.id)


class PermissionRequest(View):
    def get(self, request, user_id=None):
        if not user_id:
            return redirect('home_app:home')
        else:
            user = User.objects.get(id=user_id)
            print(user.notifications)
            notification = Notification(sender=request.user,
                                        receiver=User.objects.get(id=user_id),
                                        text='please, give me an access to your profile')
            notification.save()
            user.notifications.add(notification)
            return render(request, 'users/Message.html',
                          context={'message': 'Ваше сообщение с просьбой открытия профиля успешно отправлено'})


class PermissionAccept(View):
    def get(self, request, user_id=None):
        if not user_id:
            return redirect('home_app:home')
        else:
            user = User.objects.get(id=request.user.id)
            sender = User.objects.get(id=user_id)

            print(user.email)
            print(sender.email)

            sender.available_profiles.add(UserProfile.objects.get(user=user))
            user.save()
            Notification.objects.filter(sender=sender, is_request=True).delete()
            return redirect('users_app:notifications', request.user.id)



