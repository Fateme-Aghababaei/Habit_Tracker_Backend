from django.urls import path
from .views import add_tag, edit_tag, delete_tag, get_tag, get_user_tags, add_habit, edit_habit, delete_habit, get_habit, get_user_habits

urlpatterns = [
    path('add_tag/', add_tag, name='add_tag'),
    path('edit_tag/', edit_tag, name='edit_tag'),
    path('delete_tag/', delete_tag, name='delete_tag'),
    path('get_tag/', get_tag, name='get_tag'),
    path('get_user_tags/', get_user_tags, name='get_user_tags'),
    path('add_habit/', add_habit, name='add_habit'),
    path('edit_habit/', edit_habit, name='edit_habit'),
    path('delete_habit/', delete_habit, name='delete_habit'),
    path('get_habit/', get_habit, name='get_habit'),
    # path('get_user_habits/', get_user_habits, name='get_user_habits'),
]
