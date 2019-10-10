from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'users_app'

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('activate/<str:key>', Activate.as_view(), name='activate')
]
