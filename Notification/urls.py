from django.urls import path
from .views import get_notification, get_user_notifications, get_unread_notifications_count

urlpatterns = [
    path('get_notification/', get_notification, name='get_notification'),
    path('get_user_notifications/', get_user_notifications,
         name='get_user_notifications'),
    path('get_unread_notifications_count/', get_unread_notifications_count,
         name='get_unread_notifications_count'),
]
