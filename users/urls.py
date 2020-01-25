from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = 'users_app'

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit_profile/<int:user_id>/', EditProfileView.as_view(), name='edit_profile'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('signup/activate/<str:key>/', Activate.as_view(), name='activate'),
    path('notifications/<int:user_id>/', NotificationsView.as_view(), name='notifications'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('delete_not/<int:notification_id>', DeleteNotification.as_view(), name='delete_notification'),
    path('permission_request/<int:user_id>', PermissionRequest.as_view(), name='perm_req'),
    path('permission_accept/<int:user_id>', PermissionAccept.as_view(), name='perm_acc')
]