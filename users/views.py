from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.views import View
from .forms import *
from users.models import *
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.files.storage import default_storage
import os


class SignUp(View):
    def get(self, request):
        return render(request, 'users/signup.html')

    def post(self, request):
        form = UserForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(email=form.cleaned_data['email'],
                                            password=form.cleaned_data['password'],
                                            username=form.cleaned_data['username'],
                                            is_active=False)

            auth_key = AuthKey(key=AuthKey.gen_key(10), user=user)
            auth_key.save()
            auth_ref = request.build_absolute_uri() + 'activate/' + auth_key.key

            email = send_mail('Hello!!!',
                              'Please, confirm your registration:\n' + auth_ref,
                              'progr.0820@mail.ru',
                              [user.email],
                              fail_silently=True)

            return render(request, 'users/Message.html',
                          context={'message': 'На ваш почтовый адрес было отправлено письмо с подтверждением аккаунта!!!'})
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
            return render(request, 'users/login,html', context={'login_error': form_from_request.errors})
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
    view_name = 'users/profile.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('users_app:login')
        else:
            profile = UserProfile.objects.get(user=request.user)
            profile_form = {
                'avatar': profile.avatar,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'birth_date': profile.birth_date,
                'interests': profile.interests
            }

            for key in profile_form:
                if not profile_form[key]:
                    profile_form[key] = ""
            return render(request, self.view_name, context={'profile_form': profile_form})


class EditProfileView(ProfileView):
    view_name = 'users/edit_profile.html'

    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=UserProfile.objects.get(user=request.user))
        if form.is_valid():
            old_avatar_path = settings.MEDIA_ROOT + '\\' + str(UserProfile.objects.get(user=request.user).avatar.name)
            try:
                os.remove(old_avatar_path)
            except:
                print('can not delete old image')
            if 'avatar' in request.FILES:
                form.avatar = request.FILES['avatar']
                filename = request.FILES['avatar'].name


                form.save()
                image = Image.open(settings.MEDIA_ROOT + "\\users_avatars\\" + form.avatar.name)
                image.thumbnail((200, 200))
                os.remove(settings.MEDIA_ROOT + "\\users_avatars\\" + form.avatar.name)
                image.save(settings.MEDIA_ROOT + "\\users_avatars\\" + form.avatar.name)

            return render(request, 'users/profile.html', context={'profile_form': form.cleaned_data})
        else:
            return render(request, 'users/edit_profile.html', context={'message': form.errors})
