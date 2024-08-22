from rest_framework.decorators import api_view
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import TagSerializer, AddEditHabitSerializer, HabitSerializer, HabitInstanceSerializer, CompleteHabitSerializer
from .models import Tag, Habit, HabitInstance
from datetime import datetime, date, timedelta
from django.db.models import Q
from Profile.models import Score
from drf_yasg.utils import swagger_auto_schema  # <-- This is the important import
from drf_yasg import openapi  # <-- This is for openapi schema and parameters
from .tasks import check_for_habit_badges
from django.utils import timezone


@swagger_auto_schema(
    method='post',
    request_body=TagSerializer,
    responses={
        200: openapi.Response(
            description='Tag created successfully',
            examples={
                'application/json': {
                    'id': 1,
                    'name': 'Health',
                    'color': '#FF0000'
                }
            }
        ),
        400: openapi.Response(
            description='Invalid input',
            examples={
                'application/json': {
                    'error': 'اطلاعات واردشده صحیح نمی‌باشد.'
                }
            }
        ),
        409: openapi.Response(
            description='Duplicate tag name',
            examples={
                'application/json': {
                    'error': 'نام برچسب تکراری است.'
                }
            }
        ),
    },
    operation_description="Create a new tag for the user."
)
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


@swagger_auto_schema(
    method='post',
    request_body=TagSerializer,
    responses={
        200: openapi.Response(
            description='Tag updated successfully',
            examples={
                'application/json': {
                    'id': 1,
                    'name': 'Work',
                    'color': '#00FF00'
                }
            }
        ),
        400: openapi.Response(
            description='Invalid input',
            examples={
                'application/json': {
                    'error': 'اطلاعات واردشده صحیح نمی‌باشد.'
                }
            }
        ),
        404: openapi.Response(
            description='Tag not found',
            examples={
                'application/json': {
                    'error': 'برچسب یافت نشد.'
                }
            }
        ),
    },
    operation_description="Edit an existing tag."
)
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


@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY,
                          description="ID of the tag", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response(
            description='Tag deleted successfully',
            examples={
                'application/json': {
                    'id': 1
                }
            }
        ),
        400: openapi.Response(
            description='ID not provided or invalid',
            examples={
                'application/json': {
                    'error': 'آیدی برچسب را ارسال کنید.'
                }
            }
        ),
        404: openapi.Response(
            description='Tag not found',
            examples={
                'application/json': {
                    'error': 'برچسب یافت نشد.'
                }
            }
        ),
    },
    operation_description="Delete a specific tag by ID."
)
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


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY,
                          description="ID of the tag", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response(
            description='Tag details',
            schema=TagSerializer
        ),
        400: openapi.Response(
            description='ID not provided or invalid',
            examples={
                'application/json': {
                    'error': 'آیدی برچسب را ارسال کنید.'
                }
            }
        ),
        404: openapi.Response(
            description='Tag not found',
            examples={
                'application/json': {
                    'error': 'برچسب یافت نشد.'
                }
            }
        ),
    },
    operation_description="Retrieve details of a specific tag by ID."
)
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


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description='List of user tags',
            schema=TagSerializer(many=True)
        ),
    },
    operation_description="Retrieve all tags created by the user."
)
@api_view(['GET'])
def get_user_tags(request):
    tags = Tag.objects.filter(user=request.user)
    serializer = TagSerializer(instance=tags, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=AddEditHabitSerializer,
    responses={
        200: openapi.Response(
            description='Habit created successfully',
            schema=HabitSerializer
        ),
        400: openapi.Response(
            description='Invalid input',
            examples={
                'application/json': {
                    'error': 'اطلاعات واردشده صحیح نمی‌باشد.'
                }
            }
        ),
        404: openapi.Response(
            description='Tag not found',
            examples={
                'application/json': {
                    'error': 'برچسب یافت نشد.'
                }
            }
        ),
    },
    operation_description="Create a new habit for the user."
)
@api_view(['POST'])
def add_habit(request):
    serializer = AddEditHabitSerializer(data=request.data)
    if serializer.is_valid():
        if 'tag' in serializer.validated_data:
            tag_id = serializer.validated_data.pop('tag')
            try:
                tag = Tag.objects.get(id=tag_id, user=request.user)
            except:
                return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)
        else:
            tag = None

        if serializer.validated_data['is_repeated'] and ('repeated_days' not in serializer.validated_data or serializer.validated_data['repeated_days'] == '0000000'):
            return Response({'error': 'روزهای تکرار باید مشخص شوند.'}, status.HTTP_400_BAD_REQUEST)
        if not serializer.validated_data['is_repeated'] and 'due_date' not in serializer.validated_data:
            return Response({'error': 'تاریخ پایان باید مشخص شود.'}, status.HTTP_400_BAD_REQUEST)

        h = Habit.objects.create(
            user=request.user, tag=tag, **serializer.validated_data)
        return Response(HabitSerializer(instance=h).data, status.HTTP_200_OK)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=AddEditHabitSerializer,
    responses={
        200: openapi.Response(
            description='Habit updated successfully',
            schema=HabitSerializer
        ),
        400: openapi.Response(
            description='Invalid input',
            examples={
                'application/json': {
                    'error': 'اطلاعات واردشده صحیح نمی‌باشد.'
                }
            }
        ),
        404: openapi.Response(
            description='Habit not found',
            examples={
                'application/json': {
                    'error': 'عادت یافت نشد.'
                }
            }
        ),
    },
    operation_description="Edit an existing habit."
)
@api_view(['POST'])
def edit_habit(request):
    serializer = AddEditHabitSerializer(data=request.data)
    if serializer.is_valid() and 'id' in serializer.validated_data:
        try:
            habit = Habit.objects.get(
                id=serializer.validated_data['id'], user=request.user)
        except:
            return Response({'error': 'عادت یافت نشد.'}, status.HTTP_404_NOT_FOUND)

        if habit.from_challenge:
            if habit.from_challenge.participants.count() > 1 or habit.from_challenge.start_date <= timezone.now().date():
                return Response({'error': 'امکان ویرایش عادت‌های مربوط به چالش وجود ندارد.'}, status.HTTP_400_BAD_REQUEST)

        yesterday = timezone.now().date() - timedelta(days=1)
        weekday = (yesterday.weekday() + 2) % 7
        if habit.is_repeated and habit.modify_date <= yesterday and (habit.due_date is None or habit.due_date >= yesterday) and habit.repeated_days[weekday] == '1':
            hi, created = habit.instances.get_or_create(due_date=yesterday)

        if 'tag' in serializer.validated_data:
            tag_id = serializer.validated_data.pop('tag')
            try:
                tag = Tag.objects.get(id=tag_id, user=request.user)
            except:
                return Response({'error': 'برچسب یافت نشد.'}, status.HTTP_404_NOT_FOUND)
        else:
            tag = None

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

    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY,
                          description="ID of the habit", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response(
            description='Habit details',
            schema=HabitSerializer
        ),
        400: openapi.Response(
            description='ID not provided or invalid',
            examples={
                'application/json': {
                    'error': 'آیدی عادت را ارسال کنید.'
                }
            }
        ),
        404: openapi.Response(
            description='Habit not found',
            examples={
                'application/json': {
                    'error': 'عادت یافت نشد.'
                }
            }
        ),
    },
    operation_description="Retrieve details of a specific habit by ID."
)
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


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY,
                          description="ID of the habit instance", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response(
            description='Habit instance details',
            schema=HabitInstanceSerializer
        ),
        400: openapi.Response(
            description='ID not provided or invalid',
            examples={
                'application/json': {
                    'error': 'آیدی تکرار عادت را ارسال کنید.'
                }
            }
        ),
        404: openapi.Response(
            description='Habit instance not found',
            examples={
                'application/json': {
                    'error': 'تکرار عادت یافت نشد.'
                }
            }
        ),
    },
    operation_description="Retrieve details of a specific habit instance by ID."
)
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


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('date', openapi.IN_QUERY,
                          description="Date for which to retrieve habits (YYYY-MM-DD)", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Response(
            description='List of user habits for a specific date',
            schema=HabitInstanceSerializer(many=True)
        ),
        400: openapi.Response(
            description='Invalid date or date not provided',
            examples={
                'application/json': {
                    'error': 'تاریخ را ارسال کنید.'
                }
            }
        ),
    },
    operation_description="Retrieve all habits for a user on a specific date."
)
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
        hi, _ = HabitInstance.objects.get_or_create(
            habit=h, due_date=habit_date)
        instances.append(hi)

    for hi in passed_habit_instances:
        if hi.habit not in habits:
            instances.append(hi)

    return Response(HabitInstanceSerializer(instance=instances, many=True).data, status.HTTP_200_OK)


@api_view(['GET'])
def get_incomplete_habits_count(request):
    habit_date = timezone.now().date()

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
        hi, _ = HabitInstance.objects.get_or_create(
            habit=h, due_date=habit_date)
        instances.append(hi)

    for hi in passed_habit_instances:
        if hi.habit not in habits:
            instances.append(hi)

    count = 0
    for hi in instances:
        if not hi.is_completed:
            count += 1

    return Response({'count': count}, status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=CompleteHabitSerializer,
    responses={
        200: openapi.Response(
            description='Habit completed successfully',
            schema=HabitInstanceSerializer
        ),
        400: openapi.Response(
            description='Invalid input or habit already completed',
            examples={
                'application/json': {
                    'error': 'عادت قبلا انجام شده است.'
                }
            }
        ),
        404: openapi.Response(
            description='Habit instance not found',
            examples={
                'application/json': {
                    'error': 'تکرار عادت یافت نشد.'
                }
            }
        ),
    },
    operation_description="Mark a habit as completed for a specific date."
)
@api_view(['POST'])
def complete_habit(request):
    serializer = CompleteHabitSerializer(data=request.data)
    if serializer.is_valid():
        try:
            hi = HabitInstance.objects.get(
                habit__user=request.user, habit__id=serializer.validated_data['habit']['id'], due_date=serializer.validated_data['due_date'])
        except:
            habit = Habit.objects.get(
                user=request.user, id=serializer.validated_data['habit']['id'])
            hi = HabitInstance.objects.create(
                habit=habit, due_date=serializer.validated_data['due_date'])
        if hi.is_completed:
            return Response({'error': 'عادت قبلا انجام شده است.'}, status.HTTP_400_BAD_REQUEST)
        hi.is_completed = True
        hi.completed_date = timezone.now().date()
        hi.save()

        request.user.profile.score += hi.habit.score
        request.user.profile.completed_habits += 1
        request.user.save()

        Score.objects.create(
            user=request.user, score=hi.habit.score, type='Habit')

        has_new_badges = check_for_habit_badges(request.user)
        response = HabitInstanceSerializer(instance=hi).data
        response.update({'has_new_badge': has_new_badges})

        return Response(response, status.HTTP_200_OK)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY,
                          description="ID of the habit", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response(
            description='Habit deleted successfully',
            examples={
                'application/json': {
                    'id': 1
                }
            }
        ),
        400: openapi.Response(
            description='ID not provided or invalid',
            examples={
                'application/json': {
                    'error': 'آیدی عادت را ارسال کنید.'
                }
            }
        ),
        404: openapi.Response(
            description='Habit not found',
            examples={
                'application/json': {
                    'error': 'عادت یافت نشد.'
                }
            }
        ),
    },
    operation_description="Delete a specific habit by ID."
)
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

    if h.from_challenge:
        return Response({'error': 'امکان حذف عادت مربوط به چالش وجود ندارد.'}, status.HTTP_400_BAD_REQUEST)

    if h.is_repeated:
        yesterday = timezone.now().date() - timedelta(days=1)
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
