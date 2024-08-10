from django.urls import path
from .views import login, signup, logout, get_user, update_streak, get_follower_following, follow, unfollow, edit_profile, change_photo, get_user_brief

urlpatterns = [
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('get_user/', get_user, name='get_user'),
    path('update_streak/', update_streak, name='update_streak'),
    path('get_follower_following/', get_follower_following,
         name='get_follower_following'),
    path('follow/', follow, name='follow'),
    path('unfollow/', unfollow, name='unfollow'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('change_photo/', change_photo, name='change_photo'),
    path('get_user_brief/', get_user_brief, name='get_user_brief'),
]
