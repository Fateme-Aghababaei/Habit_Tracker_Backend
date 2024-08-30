from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


schema_view = get_schema_view(
    openapi.Info(
        title="HabitTracker API",
        default_version='v1',
        description="HabitTracker API Documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def assetlinks(request):
    with open(r'.well-known/assetlinks.json') as f:
        return HttpResponse(f, content_type='application/force-download')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('profile/', include('Profile.urls')),
    path('habit/', include('Habit.urls')),
    path('challenge/', include('Challenge.urls')),
    path('track/', include('Track.urls')),
    path('notification/', include('Notification.urls')),
    path('.well-known/assetlinks.json', assetlinks)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
