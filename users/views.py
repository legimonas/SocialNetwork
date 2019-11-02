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
            if profile_form:
                return render(request, 'users/profile.html', context={'profile_form': profile_form})
            else:
                return render(request, 'home_app/homepage.html')


class EditProfileView(View):

    def get(self, request, user_id=None):
        if not user_id:
            return redirect('home_app:home')
        else:
            profile_form = UserProfile.objects.get(user=User.objects.get(id=user_id))
            print(profile_form.first_name)
            if profile_form:
                return render(request, 'users/edit_profile.html', context={'profile_form': profile_form})
            else:
                return render(request, 'home_app/homepage.html')

    def post(self, request, user_id=None):
        form = UserProfileForm(request.POST, request.FILES, instance=UserProfile.objects.get(user=request.user))
        if form.is_valid():
            old_avatar_path = settings.MEDIA_ROOT + '\\' + str(UserProfile.objects.get(user=request.user).avatar.name)
            try:
                os.remove(old_avatar_path)
            except:
                print('can not delete old image')
            if 'avatar' in request.FILES:
                form.save(filename=request.FILES['avatar'].name)
            else:
                form.save()

            return redirect('users_app:profile', user_id)
        else:
            return render(request, 'users/edit_profile.html', context={'message': form.errors})
