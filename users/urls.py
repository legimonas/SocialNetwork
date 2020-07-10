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
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('profile/create/', ProfileCreateView.as_view(), name='profile_create'),
    path('permission_request/<int:user_id>', PermissionRequestView.as_view(), name='perm_req'),
    path('permission_accept/<int:user_id>', PermissionAcceptView.as_view(), name='perm_acc'),
    path('notifications/', NotificationsListView.as_view(), name='notifications'),
    path('notification/<int:notification_id>', NotificationView.as_view(), name='notification')
]