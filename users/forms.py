from django import forms
from django.contrib.auth.hashers import make_password, check_password
from users.models import *


class UserForm(forms.ModelForm):
    pass2 = forms.CharField(max_length=50, required=True)

    def is_valid(self):
        if not super().is_valid():
            return False
        data = self.cleaned_data

        if not ('@' in data['email']):
            self.add_error('email', 'bad format for mail')
        if not check_password(data['pass2'], data['password']):
            self.add_error('password', 'passwords don\'t match')

        if User.objects.filter(email=data['email']).exists():
            self.add_error('email', 'this email has already exist')
        return self.is_bound and not self.errors

    def clean_password(self):
        new_password = make_password(self.cleaned_data['password'])
        self.cleaned_data['password'] = new_password
        return new_password

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password'
        ]


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

    def is_valid(self):
        if not super().is_valid():
            return False
        data = self.cleaned_data
        if not ('@' in data['email']):
            self.add_error('email', 'bad format for mail')
        return self.is_bound and not self.errors


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    def save(self, filename=None, commit=True):
        default = False
        if not filename:
            default = True
            filename = '\\users_avatars\\default.jpg'
        name, extension = os.path.splitext(filename)
        profile = super(UserProfileForm, self).save(commit=False)

        profile.avatar.name = name + '__' + str(profile.id) + extension
        profile.save()
        image = None
        if default:
            image = Image.open(settings.MEDIA_ROOT + '\\users_avatars\\default.jpg')
        else:
            image = Image.open(settings.MEDIA_ROOT + '\\' + profile.avatar.name)

        image.thumbnail((200, 200))
        image.save(settings.MEDIA_ROOT + '\\' + profile.avatar.name)

    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'first_name',
            'last_name',
            'birth_date',
            'interests'
        ]
