from django.urls import path
from .views import add_challenge

urlpatterns = [
    path('add_challenge/', add_challenge, name='add_challenge'),
]
