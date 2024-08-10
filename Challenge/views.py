from rest_framework.decorators import api_view
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import AddEditChallengeSerializer, ChallengeSerializer
from .models import Challenge
from Habit.models import Habit
from django.contrib.auth.models import User
from Profile.models import Score
from datetime import date, datetime, timedelta, time
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='post',
    request_body=AddEditChallengeSerializer,
    responses={
        200: openapi.Response(description='Challenge created successfully', schema=ChallengeSerializer),
        400: openapi.Response(description='Invalid input', examples={"application/json": {"error": "اطلاعات واردشده صحیح نمی‌باشد."}})
    },
    operation_description="Create a new challenge."
)
@api_view(['POST'])
def add_challenge(request):
    serializer = AddEditChallengeSerializer(data=request.data)
    if serializer.is_valid():
        ch: Challenge = serializer.save(created_by=request.user)
        ch.participants.add(request.user)
        ch.save()

        # Create worker to reward participants
        tomorrow = ch.end_date + timedelta(days=1)
        dt = datetime.combine(tomorrow, time(6, 0, 0))
        schedule, _ = ClockedSchedule.objects.get_or_create(clocked_time=dt)
        PeriodicTask.objects.create(
            clocked=schedule,
            name=f'Challenge(id={ch.id})',
            task='Challenge.tasks.challenge_rewards',
            args=json.dumps([ch.id])
        )

        return Response(ChallengeSerializer(instance=ch).data, status.HTTP_200_OK)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'challenge_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the challenge'),
            'habit_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the habit'),
        },
        required=['challenge_id', 'habit_id']
    ),
    responses={
        200: openapi.Response(description='Habit added to challenge successfully', schema=ChallengeSerializer),
        400: openapi.Response(description='Invalid input', examples={"application/json": {"error": "اطلاعات واردشده صحیح نمی‌باشد."}}),
        404: openapi.Response(description='Not found', examples={"application/json": {"error": "عادت یافت نشد."}})
    },
    operation_description="Add a habit to an existing challenge."
)
@api_view(['POST'])
def append_habit(request):
    data = request.data
    if 'challenge_id' not in data or 'habit_id' not in data:
        return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)

    habit_id = int(data['habit_id'])
    challenge_id = int(data['challenge_id'])

    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
    except:
        return Response({'error': 'عادت یافت نشد.'}, status.HTTP_404_NOT_FOUND)

    try:
        challenge = Challenge.objects.get(
            id=challenge_id, created_by=request.user)
    except:
        return Response({'error': 'چالش یافت نشد.'}, status.HTTP_404_NOT_FOUND)

    habit.from_challenge = True
    habit.save()
    challenge.habits.add(habit)
    challenge.save()
    return Response(ChallengeSerializer(instance=challenge).data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=AddEditChallengeSerializer,
    responses={
        200: openapi.Response(description='Challenge edited successfully', schema=ChallengeSerializer),
        400: openapi.Response(description='Invalid input', examples={"application/json": {"error": "اطلاعات واردشده صحیح نمی‌باشد."}}),
        404: openapi.Response(description='Not found', examples={"application/json": {"error": "چالش یافت نشد."}})
    },
    operation_description="Edit an existing challenge."
)
@api_view(['POST'])
def edit_challenge(request):
    if 'id' not in request.data:
        return Response({'error': 'آیدی چالش را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(request.data['id'])
    try:
        ch = Challenge.objects.get(id=id)
    except:
        return Response({'error': 'چالش یافت نشد.'}, status.HTTP_404_NOT_FOUND)
    if ch.participants.count() > 1 or ch.start_date <= date.today():
        return Response({'error': 'با توجه به ثبت‌نام کاربران، امکان ویرایش وجود ندارد.'}, status.HTTP_400_BAD_REQUEST)

    tomorrow = ch.end_date + timedelta(days=1)
    dt = datetime.combine(tomorrow, time(6, 0, 0))
    schedule, _ = ClockedSchedule.objects.get_or_create(clocked_time=dt)
    task = PeriodicTask.objects.get(name=f'Challenge(id={ch.id})')
    task.clocked = schedule
    task.save()

    serializer = AddEditChallengeSerializer(
        instance=ch, data=request.data, partial=True)
    if serializer.is_valid():
        ch = serializer.save()
        return Response(ChallengeSerializer(instance=ch).data, status.HTTP_200_OK)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'challenge_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the challenge'),
            'habit_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the habit'),
        },
        required=['challenge_id', 'habit_id']
    ),
    responses={
        200: openapi.Response(description='Habit removed from challenge successfully', schema=ChallengeSerializer),
        400: openapi.Response(description='Invalid input', examples={"application/json": {"error": "اطلاعات واردشده صحیح نمی‌باشد."}}),
        404: openapi.Response(description='Not found', examples={"application/json": {"error": "چالش یافت نشد."}})
    },
    operation_description="Remove a habit from a challenge."
)
@api_view(['POST'])
def remove_habit(request):
    data = request.data
    if 'challenge_id' not in data or 'habit_id' not in data:
        return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)

    habit_id = int(data['habit_id'])
    challenge_id = int(data['challenge_id'])

    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
    except:
        return Response({'error': 'عادت یافت نشد.'}, status.HTTP_404_NOT_FOUND)

    try:
        challenge = Challenge.objects.get(
            id=challenge_id, created_by=request.user)
    except:
        return Response({'error': 'چالش یافت نشد.'}, status.HTTP_404_NOT_FOUND)

    if challenge.participants.count() > 1 or challenge.start_date <= date.today():
        return Response({'error': 'امکان حذف عادت وجود ندارد.'}, status.HTTP_400_BAD_REQUEST)

    challenge.habits.remove(habit)
    challenge.save()
    habit.delete()
    return Response(ChallengeSerializer(instance=challenge).data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description="ID of the challenge", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response(description='Successfully participated in challenge', schema=ChallengeSerializer),
        400: openapi.Response(description='Invalid input or insufficient score', examples={"application/json": {"error": "امتیاز شما برای شرکت در چالش کم است."}}),
        404: openapi.Response(description='Not found', examples={"application/json": {"error": "چالش یافت نشد."}}),
        409: openapi.Response(description='Conflict', examples={"application/json": {"error": "کاربر قبلا در چالش ثبت‌نام کرده است."}})
    },
    operation_description="Participate in a challenge."
)
@api_view(['POST'])
def participate(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی چالش را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)

    try:
        ch = Challenge.objects.get(id=id)
    except:
        return Response({'error': 'چالش یافت نشد.'}, status.HTTP_404_NOT_FOUND)

    user: User = request.user
    if user in ch.participants.all():
        return Response({'error': 'کاربر قبلا در چالش ثبت‌نام کرده است.'}, status.HTTP_409_CONFLICT)

    if ch.price > user.profile.score:
        return Response({'error': 'امتیاز شما برای شرکت در چالش کم است.', 'required': ch.price, 'user_score': user.profile.score}, status.HTTP_400_BAD_REQUEST)

    user.profile.score -= ch.price
    user.save()
    Score.objects.create(user=user, score=-ch.price, type='Challenge Price')

    ch.participants.add(user)
    ch.save()

    for habit in ch.habits.all():
        # Make a copy of habit for the user
        habit.pk = None
        habit.user = user
        habit.save()

    return Response(ChallengeSerializer(instance=ch).data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description="ID of the challenge", type=openapi.TYPE_INTEGER),
        openapi.Parameter('code', openapi.IN_QUERY, description="Share code of the challenge", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Response(description='Challenge details', schema=ChallengeSerializer),
        400: openapi.Response(description='Invalid input', examples={"application/json": {"error": "آیدی یا کد چالش را ارسال کنید."}}),
        404: openapi.Response(description='Not found', examples={"application/json": {"error": "چالش یافت نشد."}})
    },
    operation_description="Get details of a specific challenge by ID or code."
)
@api_view(['GET'])
def get_challenge(request):
    id = request.GET.get('id')
    code = request.GET.get('code')

    if id is None and code is None:
        return Response({'error': 'آیدی یا کد چالش را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)

    if id is not None and code is not None:
        return Response({'error': 'فقط یکی از موارد آیدی یا کد را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)

    try:
        if id is not None:
            ch = Challenge.objects.get(id=int(id))
        else:
            ch = Challenge.objects.get(share_code=code)
    except:
        return Response({'error': 'چالش یافت نشد.'}, status.HTTP_404_NOT_FOUND)

    return Response(ChallengeSerializer(instance=ch).data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(description='List of active public challenges', schema=ChallengeSerializer(many=True))
    },
    operation_description="Get a list of all active public challenges."
)
@api_view(['GET'])
def get_active_challenges(request):
    challenges = Challenge.objects.filter(
        is_public=True, end_date__gte=date.today())
    return Response(ChallengeSerializer(instance=challenges, many=True).data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('active', openapi.IN_QUERY, description="Filter by active status ('true' or 'false')", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Response(description='List of challenges created by the user', schema=ChallengeSerializer(many=True))
    },
    operation_description="Get a list of challenges created by the user, optionally filtering by active status."
)
@api_view(['GET'])
def get_owned_challenges(request):
    challenges = Challenge.objects.filter(created_by=request.user)
    active = request.GET.get('active')
    if active is not None:
        if active == 'true':
            challenges = challenges.filter(end_date__gte=date.today())
        elif active == 'false':
            challenges = challenges.filter(end_date__lt=date.today())

    return Response(ChallengeSerializer(instance=challenges, many=True).data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('active', openapi.IN_QUERY, description="Filter by active status ('true' or 'false')", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Response(description='List of challenges the user is participating in', schema=ChallengeSerializer(many=True))
    },
    operation_description="Get a list of challenges the user is participating in, optionally filtering by active status."
)
@api_view(['GET'])
def get_participated_challenges(request):
    challenges = Challenge.objects.filter(participants=request.user)
    active = request.GET.get('active')
    if active is not None:
        if active == 'true':
            challenges = challenges.filter(end_date__gte=date.today())
        elif active == 'false':
            challenges = challenges.filter(end_date__lt=date.today())

    return Response(ChallengeSerializer(instance=challenges, many=True).data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description="ID of the challenge", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response(description='Challenge deleted successfully', examples={"application/json": {"id": 1}}),
        400: openapi.Response(description='Invalid input or challenge cannot be deleted', examples={"application/json": {"error": "امکان حذف چالش وجود ندارد."}}),
        404: openapi.Response(description='Not found', examples={"application/json": {"error": "چالش یافت نشد."}})
    },
    operation_description="Delete a specific challenge by ID."
)
@api_view(['DELETE'])
def delete_challenge(request):
    id = request.GET.get('id')
    if id is None:
        return Response({'error': 'آیدی چالش را ارسال کنید.'}, status.HTTP_400_BAD_REQUEST)
    id = int(id)
    try:
        ch = Challenge.objects.get(id=id, created_by=request.user)
    except:
        return Response({'error': 'چالش یافت نشد.'}, status.HTTP_404_NOT_FOUND)

    if ch.participants.count() > 1 or ch.start_date <= date.today():
        return Response({'error': 'امکان حذف چالش وجود ندارد.'}, status.HTTP_400_BAD_REQUEST)

    for h in ch.habits.all():
        h.delete()

    ch.delete()
    return Response({'id': id}, status.HTTP_200_OK)
