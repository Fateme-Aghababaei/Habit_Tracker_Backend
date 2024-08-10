from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="HabitTracker API",
        default_version='v1',
        description="HabitTracker API Documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),    path('profile/', include('Profile.urls')),
    path('habit/', include('Habit.urls')),
    path('challenge/', include('Challenge.urls')),
    path('track/', include('Track.urls')),
]
