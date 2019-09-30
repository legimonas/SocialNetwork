from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.views import View
from users.models import *
from django.contrib.auth import authenticate, login, logout
import random, string

# Create your views here.
def gen_key(n):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(n))


class SignUp(View):
    def get(self, request):
        return render(request, 'users/signup.html')
    def post(self, request):
        form = {'username': request.POST['username'],
                'mail': request.POST['mail'],
                'password': request.POST['password'],}


        errors = {}
        if not form['username']:
            errors['name_ex'] = ['username must be set']
        if not form['mail']:
            errors['mail_ex'] = ['email must be set']

        if User.objects.filter(email=form['mail']).exists():
            errors['mail_ex'] = ['this email has already exist']

        if errors:
            return render(request, 'users/signup.html', context={'errors': errors, 'form': form})

        user = User.objects.create_user(email=form['mail'],
                                        password=form['password'],
                                        username=form['username'],
                                        is_active=False)
        akey = AuthKey(key=gen_key(10), user=user)
        akey.save()
        auth_ref = 'http://'+str(get_current_site(request))+'/users/activate/'+akey.key

        email = send_mail('Hello!!!', 'Please, confirm your registration:\n'+auth_ref, 'legimonas1000@gmail.com', [user.email], fail_silently=True)

        return render(request, 'users/Message.html', context={'message': 'На ваш почтовый адрес было отправлено письмо с подтверждением аккаунта!!!'})
        #return render(request, 'users/edit_profile.html', context={'errors': errors, 'form': form})


class Login(View):
    def get(self, request):

        return render(request, 'users/login.html')

    def post(self, request):
        form = {'mail': request.POST['mail'],
                'password': request.POST['password'],}

        user = authenticate(email=form['mail'], password=form['password'])

        if user is not None:
            login(request, user)
            return redirect('home_app:home')
        else:
            return render(request, 'users/login.html', context={'login_error': 'Неверная почта или пароль'})

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('home_app:home')



class Profile(View):
    user_id = int()
    def get(self, request):
        pass

    def post(self, request):
        profile_form = {}
        profile_form['first_name'] = request.POST['first_name']
        profile_form['last_name'] = request.POST['last_name']
        profile_form['birth_date'] = request.POST['birth_date']
        profile_form['interests'] = request.POST['interests']


class Activate(View):
    def get(self, request, key):

        authKey = AuthKey.safe_get(key=key)
        print(authKey.key)
        if authKey is not None:
            user = authKey.user
            print(user)
            user.is_active = True
            user.save()
            authKey.delete()
        return redirect('users_app:login')
