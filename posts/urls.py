from django.urls import path
from .views import *


app_name = 'posts_app'

urlpatterns = [
    path('create/', PostCreate.as_view(), name='create'),
]