from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'users_app'

urlpatterns = [
    path('profile/<int:user_id>', ProfileView.as_view(), name='profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login')
]