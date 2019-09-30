from django.contrib import admin
from django.urls import path, include
from .views import home

app_name = 'home_app'

urlpatterns = [
    path('', home.as_view(), name='home'),

]