from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.views import View
from .forms import *
from users.models import *
from django.contrib.auth import authenticate, login, logout


class SignUp(View):
    def get(self, request):
        return render(request, 'users/signup.html')

    def post(self, request):
        form_from_request = UserForm(request.POST)
        form = {}
        if form_from_request.is_valid():
            form = form_from_request.cleaned_data
        else:
            return render(request, 'users/signup.html')
        print(form)

        errors = {}
        if not form['username']:
            errors['name_ex'] = ['username must be set']
        if not form['email']:
            errors['mail_ex'] = ['email must be set']

        if User.objects.filter(email=form['email']).exists():
            errors['mail_ex'] = ['this email has already exist']

        if errors:
            return render(request, 'users/signup.html', context={'errors': errors, 'form': form})

        user = User.objects.create_user(email=form['email'],
                                        password=form['password'],
                                        username=form['username'],
                                        is_active=False)

        auth_key = AuthKey(key=AuthKey.gen_key(10), user=user)
        auth_key.save()
        auth_ref = 'http://' + str(get_current_site(request)) + '/users/activate/' + auth_key.key

        email = send_mail('Hello!!!',
                          'Please, confirm your registration:\n' + auth_ref,
                          'progr.0820@mail.ru',
                          [user.email],
                          fail_silently=True)

        return render(request, 'users/Message.html',
                      context={'message': 'На ваш почтовый адрес было отправлено письмо с подтверждением аккаунта!!!'})
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
        print(form)
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
        print(auth_key.key)
        if auth_key is not None:
            user = auth_key.user
            print(user)
            user.is_active = True
            user.save()
            auth_key.delete()
        return redirect('users_app:login')


class EditProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('users_app:login')
        else:
            profile = UserProfile.objects.get(user=request.user)
            profile_form = {'first_name': profile.first_name,
                            'last_name': profile.last_name,
                            'birth_date': profile.birth_date,
                            'interests': profile.interests}
            for key in profile_form:
                if not profile_form[key]:
                    profile_form[key] = ""
            return render(request, 'users/edit_profile.html', context={'profile_form': profile_form})

    def post(self, request):
        edit_form = {'first_name': request.POST['first_name'],
                     'last_name': request.POST['last_name'],
                     'birth_date': request.POST['birth_date'],
                     'interests': request.POST['interests']}
        profile = UserProfile()
        if UserProfile.objects.filter(user=request.user).exists():
            profile = UserProfile.objects.get(user=request.user)
            profile.set_profile_from_form(**edit_form)
        else:
            profile = UserProfile.get_profile_from_form(**edit_form)
        profile.save()

        return render(request, 'users/edit_profile.html', context={'profile_form': edit_form})
