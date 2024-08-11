from rest_framework.decorators import api_view
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
def get_notification(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی اعلان را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)
    try:
        notif = Notification.objects.get(id=id, user=request.user)
        return Response(NotificationSerializer(instance=notif).data, status.HTTP_200_OK)
    except:
        return Response({'error': 'اعلان یافت نشد.'}, status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_user_notifications(request):
    page = int(request.GET.get('page', 1))
    item_per_page = int(request.GET.get('item_per_page', 7))

    notifications = request.user.notifications.order_by(
        '-created_at')[(page-1)*item_per_page: page*item_per_page]

    for notif in notifications:
        notif.is_read = True
        notif.save()

    return Response(NotificationSerializer(instance=notifications, many=True).data, status.HTTP_200_OK)


@api_view(['GET'])
def get_unread_notifications_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return Response({'count': count}, status.HTTP_200_OK)
