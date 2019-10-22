from django import forms
from .models import *


class UserForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)
    pass2 = forms.CharField(max_length=50)

    def is_valid(self):
        if not super().is_valid():
            return False
        data = self.cleaned_data

        if not ('@' in data['email']):
            self.add_error('email', 'bad format for mail')
        if data['password'] != data['pass2']:
            self.add_error('password', 'passwords don\'t match')


        if User.objects.filter(email=data['email']).exists():
            self.add_error('email', 'this email has already exist')
        return self.is_bound and not self.errors


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

    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'first_name',
            'last_name',
            'birth_date',
            'interests'
        ]
