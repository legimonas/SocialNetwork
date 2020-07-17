from django.urls import path
from posts.views import *

app_name = 'posts_app'

urlpatterns = [
    path('create/', PostView.as_view(), name='create'),
    path('<int:post_id>/', PostView.as_view(), name='get'),
    path('like/<int:post_id>/', PostLikeView.as_view(), name='like'),
    path('funs/<int:post_id>/', PostFunsListView.as_view(), name='funs'),
    path('recommendations/', RecommendationsListView.as_view(), name='recommendations'),
    path('user/<int:user_id>', PostsListByUserView.as_view(), name='user_articles'),
    path('user/', PostsListByUserView.as_view(), name='user_articles'),
]