from rest_framework.decorators import api_view
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import TagSerializer, AddEditHabitSerializer, HabitSerializer, HabitInstanceSerializer, CompleteHabitSerializer
from .models import Tag, Habit, HabitInstance
from datetime import datetime, date, timedelta
from django.db.models import Q
from Profile.models import Score


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
def get_habit_instance(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی تکرار عادت را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)
    try:
        habit_instance = HabitInstance.objects.get(
            id=id, habit__user=request.user)
        return Response(HabitInstanceSerializer(instance=habit_instance).data, status.HTTP_200_OK)
    except:
        return Response({'error': 'تکرار عادت یافت نشد.'}, status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_user_habits(request):
    habit_date = request.GET.get('date')
    if habit_date is None:
        return Response({'error': 'تاریخ را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    try:
        habit_date = datetime.strptime(habit_date, '%Y-%m-%d').date()
    except:
        return Response({'error': 'تاریخ معتبر نیست.'}, status.HTTP_400_BAD_REQUEST)

    weekday = (habit_date.weekday() + 2) % 7

    # Passed Repeated Habits
    passed_habit_instances = HabitInstance.objects.filter(habit__user=request.user, habit__is_repeated=True,
                                                          habit__start_date__lte=habit_date, habit__modify_date__gt=habit_date, due_date=habit_date)

    # Repeated Habits
    repeated_habits = Habit.objects.filter(Q(user=request.user), Q(is_repeated=True), Q(modify_date__lte=habit_date), Q(
        due_date=None) | Q(due_date__gte=habit_date)).filter(repeated_days__regex='^\d{'+str(weekday)+'}1\d{'+str(6-weekday)+'}$')

    # Non-Repeated Habits
    non_repeated_habits = Habit.objects.filter(
        user=request.user, is_repeated=False, due_date=habit_date)

    habits = repeated_habits.union(non_repeated_habits)
    instances = []
    for h in habits:
        try:
            hi = h.instances.get(due_date=habit_date)
        except:
            hi = HabitInstance(habit=h, due_date=habit_date)
        instances.append(hi)

    for hi in passed_habit_instances:
        if hi.habit not in habits:
            instances.append(hi)

    return Response(HabitInstanceSerializer(instance=instances, many=True).data, status.HTTP_200_OK)


@api_view(['POST'])
def complete_habit(request):
    serializer = CompleteHabitSerializer(data=request.data)
    if serializer.is_valid():
        print(serializer.validated_data)
        hi, _ = HabitInstance.objects.get_or_create(
            habit__user=request.user, habit__id=serializer.validated_data['habit']['id'], due_date=serializer.validated_data['due_date'])
        if hi.is_completed:
            return Response({'error': 'عادت قبلا انجام شده است.'}, status.HTTP_400_BAD_REQUEST)
        hi.is_completed = True
        hi.completed_date = date.today()
        hi.save()

        request.user.profile.score += hi.habit.score
        request.user.save()

        Score.objects.create(
            user=request.user, score=hi.habit.score, type='Habit')

        return Response(HabitInstanceSerializer(instance=hi).data, status.HTTP_200_OK)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_habit(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی عادت را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)
    try:
        h = Habit.objects.get(id=id, user=request.user)
    except:
        return Response({'error': 'عادت یافت نشد.'}, status.HTTP_404_NOT_FOUND)

    if h.is_repeated:
        yesterday = date.today() - timedelta(days=1)
        h.due_date = yesterday
        h.save()
        return Response({'id': id}, status.HTTP_200_OK)
    else:
        hi: HabitInstance = h.instances.first()
        if hi is None or not hi.is_completed:
            h.delete()
            if hi is not None:
                hi.delete()
            return Response({'id': id}, status.HTTP_200_OK)
        return Response({'error': 'امکان حذف عادت انجام شده وجود ندارد.'}, status.HTTP_400_BAD_REQUEST)
