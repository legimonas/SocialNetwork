from django.urls import path
from .views import *


app_name = 'posts_app'

urlpatterns = [
    path('create/', PostCreate.as_view(), name='create'),
    path('get/', PostsGet.as_view(), name='get'),
    path('get/<int:post_id>', PostsGet.as_view(), name='get'),
    path('like/<int:post_id>', PostLike.as_view(), name='like'),
    path('funs/<int:post_id>', PostFunsList.as_view(), name='funs'),
    path('recommendations/', Recommendations.as_view(), name='recommendations'),
    path('user_articles/<int:user_id>', GetPostsByUser.as_view(), name='user_articles')
]