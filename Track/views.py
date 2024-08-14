from .models import Track
from Habit.models import Tag
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import AddTrackSerializer, TrackSerializer, EditTrackSerializer, FinishTrackSerializer, TrackListSerializer
from django.db.models import F


@api_view(['POST'])
def add_track(request):
    serializer = AddTrackSerializer(data=request.data)
    if serializer.is_valid():
        if 'tag' in serializer.validated_data:
            tag_id = serializer.validated_data['tag']
            try:
                tag = Tag.objects.get(id=tag_id, user=request.user)
            except:
                return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)
        else:
            tag = None
        track = Track.objects.create(
            user=request.user,
            name=serializer.validated_data['name'],
            tag=tag,
            start_datetime=serializer.validated_data['start_datetime']
        )
        if 'end_datetime' in serializer.validated_data:
            track.end_datetime = serializer.validated_data['end_datetime']
            track.save()
        return Response(TrackSerializer(instance=track).data, status.HTTP_200_OK)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def edit_track(request):
    serializer = EditTrackSerializer(data=request.data)
    if serializer.is_valid():
        id = serializer.validated_data['id']
        try:
            track = Track.objects.get(id=id, user=request.user)
            track.name = serializer.validated_data['name']
            if 'tag' in serializer.validated_data:
                tag_id = serializer.validated_data['tag']
                try:
                    tag = Tag.objects.get(id=tag_id, user=request.user)
                except:
                    return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)
            else:
                tag = None
            track.tag = tag
            track.save()
            return Response(TrackSerializer(instance=track).data, status.HTTP_200_OK)
        except:
            return Response({'error': 'ردیابی یافت نشد.'}, status.HTTP_404_NOT_FOUND)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def finish_track(request):
    serializer = FinishTrackSerializer(data=request.data)
    if serializer.is_valid():
        id = serializer.validated_data['id']
        try:
            track = Track.objects.get(id=id, user=request.user)
            dt = serializer.validated_data['end_datetime']
            if dt <= track.start_datetime:
                return Response({'error': 'زمان پایان نباید قبل از زمان شروع باشد.'}, status.HTTP_400_BAD_REQUEST)
            track.end_datetime = dt
            track.save()
            return Response(TrackSerializer(instance=track).data, status.HTTP_200_OK)
        except:
            return Response({'error': 'ردیابی یافت نشد.'}, status.HTTP_404_NOT_FOUND)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_track(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی ردیابی را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)
    try:
        track = Track.objects.get(id=id, user=request.user)
        return Response(TrackSerializer(instance=track).data, status.HTTP_200_OK)
    except:
        return Response({'error': 'ردیابی یافت نشد.'}, status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_user_tracks(request):
    page = int(request.GET.get('page', 1))
    item_per_page = int(request.GET.get('item_per_page', 7))
    dates = Track.objects.filter(user=request.user).values(
        date=F('start_datetime__date')).distinct().order_by('-date')[(page-1)*item_per_page: page*item_per_page]
    data = [{
        'date': date['date'],
        'tracks': Track.objects.filter(user=request.user, start_datetime__date=date['date']).order_by('-start_datetime')
    } for date in dates]
    serializer = TrackListSerializer(data, many=True)
    return Response(serializer.data, status.HTTP_200_OK)
