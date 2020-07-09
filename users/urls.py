from django.urls import path
from users.views import *

app_name = 'users_app'

urlpatterns = [
    path('profile/<int:user_id>', ProfileView.as_view(), name='profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/activate/<str:key>/', ActivateView.as_view(), name='activate'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile')
]