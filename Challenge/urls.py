from django.urls import path
from .views import add_challenge, append_habit, edit_challenge, remove_habit, participate, get_challenge, get_active_challenges, get_owned_challenges, get_participated_challenges, delete_challenge

urlpatterns = [
    path('add_challenge/', add_challenge, name='add_challenge'),
    path('append_habit/', append_habit, name='append_habit'),
    path('edit_challenge/', edit_challenge, name='edit_challenge'),
    path('remove_habit/', remove_habit, name='remove_habit'),
    path('participate/', participate, name='participate'),
    path('get_challenge/', get_challenge, name='get_challenge'),
    path('get_active_challenges/', get_active_challenges,
         name='get_active_challenges'),
    path('get_owned_challenges/', get_owned_challenges,
         name='get_owned_challenges'),
    path('get_participated_challenges/', get_participated_challenges,
         name='get_participated_challenges'),
    path('delete_challenge/', delete_challenge, name='delete_challenge'),
]
