from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/', include('Profile.urls')),
    path('habit/', include('Habit.urls')),
    path('challenge/', include('Challenge.urls')),
    path('track/', include('Track.urls')),
]
