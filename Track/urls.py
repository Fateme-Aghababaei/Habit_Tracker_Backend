from django.urls import path
from .views import add_track, edit_track, finish_track, get_track, get_user_tracks

urlpatterns = [
    path('add_track/', add_track, name='add_track'),
    path('edit_track/', edit_track, name='edit_track'),
    path('finish_track/', finish_track, name='finish_track'),
    path('get_track/', get_track, name='get_track'),
    path('get_user_tracks/', get_user_tracks, name='get_user_tracks'),
]
