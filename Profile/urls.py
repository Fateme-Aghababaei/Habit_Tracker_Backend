from django.urls import path
from .views import login, signup, logout, get_user

urlpatterns = [
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('get_user/', get_user, name='get_user'),
]
