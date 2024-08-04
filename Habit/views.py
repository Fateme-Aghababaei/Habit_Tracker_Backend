from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import TagSerializer, AddEditHabitSerializer, HabitSerializer
from .models import Tag, Habit
from datetime import datetime
from django.db.models.functions import Substr
from django.db.models import F, BooleanField


@api_view(['POST'])
def add_tag(request):
    serializer = TagSerializer(data=request.data)
    if serializer.is_valid():
        tag, created = Tag.objects.get_or_create(
            name=serializer.validated_data['name'],
            color=serializer.validated_data['color'],
            user=request.user
        )
        if created:
            return Response({
                'id': tag.id, 'name': tag.name, 'color': tag.color
            }, status.HTTP_200_OK)
        return Response({'error': 'نام برچسب تکراری است.'}, status.HTTP_409_CONFLICT)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def edit_tag(request):
    serializer = TagSerializer(data=request.data)
    if serializer.is_valid():
        try:
            tag = Tag.objects.get(
                id=serializer.validated_data['id'], user=request.user)
            tag.name = serializer.validated_data['name']
            tag.color = serializer.validated_data['color']
            tag.save()
            return Response({
                'id': tag.id, 'name': tag.name, 'color': tag.color
            }, status.HTTP_200_OK)
        except:
            return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_tag(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی برچسب را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)
    try:
        tag = Tag.objects.get(id=id, user=request.user)
        tag.delete()
        return Response({
            'id': id
        }, status.HTTP_200_OK)
    except:
        return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_tag(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی برچسب را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)
    try:
        tag = Tag.objects.get(id=id, user=request.user)
        return Response(TagSerializer(instance=tag).data, status.HTTP_200_OK)
    except:
        return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_user_tags(request):
    tags = Tag.objects.filter(user=request.user)
    serializer = TagSerializer(instance=tags, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['POST'])
def add_habit(request):
    serializer = AddEditHabitSerializer(data=request.data)
    if serializer.is_valid():
        tag_id = serializer.validated_data.pop('tag')
        try:
            tag = Tag.objects.get(id=tag_id, user=request.user)
        except:
            return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)

        if serializer.validated_data['is_repeated'] and ('repeated_days' not in serializer.validated_data or serializer.validated_data['repeated_days'] == '0000000'):
            return Response({'error': 'روزهای تکرار باید مشخص شوند.'}, status.HTTP_400_BAD_REQUEST)
        if not serializer.validated_data['is_repeated'] and 'due_date' not in serializer.validated_data:
            return Response({'error': 'تاریخ پایان باید مشخص شود.'}, status.HTTP_400_BAD_REQUEST)

        h = Habit.objects.create(
            user=request.user, tag=tag, **serializer.validated_data)
        return Response(HabitSerializer(instance=h).data, status.HTTP_200_OK)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def edit_habit(request):
    serializer = AddEditHabitSerializer(data=request.data)
    if serializer.is_valid() and 'id' in serializer.validated_data:
        try:
            habit = Habit.objects.get(
                id=serializer.validated_data['id'], user=request.user)
            tag_id = serializer.validated_data.pop('tag')
            try:
                tag = Tag.objects.get(id=tag_id, user=request.user)
            except:
                return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)

            if serializer.validated_data['is_repeated'] and ('repeated_days' not in serializer.validated_data or serializer.validated_data['repeated_days'] == '0000000'):
                return Response({'error': 'روزهای تکرار باید مشخص شوند.'}, status.HTTP_400_BAD_REQUEST)
            if not serializer.validated_data['is_repeated'] and 'due_date' not in serializer.validated_data:
                return Response({'error': 'تاریخ پایان باید مشخص شود.'}, status.HTTP_400_BAD_REQUEST)

            habit.name = serializer.validated_data['name']
            habit.description = serializer.validated_data['description']
            habit.tag = tag
            if 'due_date' in serializer.validated_data:
                habit.due_date = serializer.validated_data['due_date']
            else:
                habit.due_date = None
            habit.is_repeated = serializer.validated_data['is_repeated']
            if 'repeated_days' in serializer.validated_data:
                habit.repeated_days = serializer.validated_data['repeated_days']
            else:
                habit.repeated_days = None
            habit.save()
            return Response(HabitSerializer(instance=habit).data, status.HTTP_200_OK)
        except:
            return Response({'error': 'عادت یافت نشد.'}, status.HTTP_404_NOT_FOUND)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_habit(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی عادت را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    habit_id = int(id)
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
        habit.delete()
        return Response({'id': habit_id}, status.HTTP_200_OK)
    except:
        return Response({'error': 'عادت یافت نشد.'}, status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_habit(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی عادت را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)
    try:
        habit = Habit.objects.get(id=id, user=request.user)
        return Response(HabitSerializer(instance=habit).data, status.HTTP_200_OK)
    except:
        return Response({'error': 'عادت یافت نشد.'}, status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_user_habits(request):
    habit_date = request.GET.get('date')
    if habit_date is None:
        return Response({'error': 'تاریخ را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    try:
        habit_date = datetime.strptime(habit_date, '%Y-%m-%d').date()
    except:
        return Response({'error': 'تاریخ معتبر نیست.'}, status.HTTP_400_BAD_REQUEST)

    weekday = (habit_date.weekday + 2) % 7

    # Repeated Habits
    Habit.objects.filter(user=request.user, is_repeated=True,
                         due_date__gte=habit_date).annotate(week_day=Substr(F('repeated_days'), weekday), output_filed=BooleanField()).filter(week_day=True)

    return Response({})
