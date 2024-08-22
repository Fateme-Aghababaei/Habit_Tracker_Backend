from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from .serializers import LoginSerializer, ShortProfileSerializer, UserSerializer, FollowerFollowingSerializer, EditUserInfoSerializer, ChangePhotoSerializer, LoginResponseSerializer, UserBadgeSerializer
from django.contrib.auth import authenticate, login as DjangoLogin, logout as DjangoLogout
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from datetime import timedelta
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from Notification.models import Notification
from .tasks import check_for_streak_badges
from Profile.models import UserBadge, Score
from django.utils import timezone
from Habit.models import HabitInstance, Habit, Tag
from Habit.serializers import TagSerializer
from django.db.models import Q, F, Sum, Count
from Track.models import Track


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request):
    # TODO Add daily login reward
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        # user = authenticate(email=email, password=password)
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                DjangoLogin(request, user=user)
                token, created = Token.objects.get_or_create(user=user)
                return Response(LoginResponseSerializer({
                    'token': token.key,
                    'username': user.username
                }).data, status.HTTP_200_OK)
            else:
                raise user.DoesNotExist()
        except:
            return Response({'error': 'نام کاربری یا رمز عبور نادرست است.'}, status.HTTP_404_NOT_FOUND)
    return Response({'error': 'اطلاعات صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def logout(request):
    user = request.user
    Token.objects.get(user_id=user.id).delete()
    DjangoLogout(request)
    return Response({}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup(request):
    # TODO add score in case of inviter
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        if User.objects.filter(email=email):
            return Response({"error": "کاربری با این ایمیل وجود دارد."}, status.HTTP_409_CONFLICT)

        username = f'user#{get_random_string(8)}'.lower()
        while User.objects.filter(username__iexact=username):
            username = f'user#{get_random_string(8)}'.lower()

        inviter = None  # Initialize inviter to None
        try:
            if 'inviter' in serializer.validated_data:
                inviter_username = serializer.validated_data['inviter']
                inviter = User.objects.get(username=inviter_username)
        except:
            return Response({'error': 'معرف پیدا نشد.'}, status.HTTP_404_NOT_FOUND)

        user = User.objects.create_user(
            username=username, email=email, password=password)
        token, created = Token.objects.get_or_create(user=user)

        user.profile.streak_start = timezone.now().date()
        user.profile.streak_end = timezone.now().date()
        user.profile.notif_enabled = False
        user.first_name = username
        if 'inviter' in serializer.validated_data:
            user.profile.inviter = inviter

        if inviter:
            signup_score = 300
        else:
            signup_score = 100

        user.profile.score += signup_score
        Score.objects.create(user=user, score=signup_score, type='Sign Up')

        user.save()
        DjangoLogin(request, user=user)

        return Response({
            'token': token.key,
            'username': user.username,
        })
    return Response({'error': 'اطلاعات صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)

# TODO change password view


@api_view(['GET'])
def get_user(request):
    username = request.GET.get('username')
    if username:
        try:
            user: User = User.objects.get(username=username)
        except:
            return Response({'error': 'کاربر یافت نشد.'}, status.HTTP_404_NOT_FOUND)
    else:
        user: User = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
def update_streak(request):
    user: User = request.user
    date_diff = (timezone.now().date() - user.profile.streak_end).days
    if date_diff > 1:
        user.profile.streak_start = timezone.now().date()
        user.profile.streak_end = timezone.now().date()
        # streak = 1
        state = 'reset'
    elif date_diff == 1:
        user.profile.streak_end = timezone.now().date()
        # streak = (user.profile.streak_end - user.profile.streak_start).days + 1
        state = 'increased'
    else:
        state = 'unchanged'

    streak = (user.profile.streak_end - user.profile.streak_start).days + 1
    user.save()
    has_new_badges = check_for_streak_badges(user)

    if not has_new_badges:
        if UserBadge.objects.filter(profile__user=user, is_new=True):
            has_new_badges = True

    return Response({
        'streak': streak,
        'state': state,
        'has_new_badges': has_new_badges
    }, status.HTTP_200_OK)


@api_view(['GET'])
def get_follower_following(request):
    username = request.GET.get('username')
    if username:
        user: User = User.objects.get(username=username)
    else:
        user: User = request.user

    serializer = FollowerFollowingSerializer(instance=user)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['POST'])
def follow(request):
    try:
        if 'username' in request.data:
            user: User = User.objects.get(username=request.data['username'])
        else:
            return Response({'error': 'نام کاربری وارد نشده است.'}, status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'error': 'نام کاربری وارد شده صحیح نیست.'}, status.HTTP_404_NOT_FOUND)

    if request.user in user.profile.followers:
        return Response({'error': 'کاربر قبلا دنبال شده‌است.'}, status.HTTP_400_BAD_REQUEST)

    user.profile.followers.add(request.user)

    Notification.objects.create(user=user, title='دنبال‌کننده جدید',
                                description=f'کاربر {request.user.first_name} شما را دنبال کرد.')
    # TODO push notification if needed
    return Response({}, status.HTTP_200_OK)


@api_view(['POST'])
def unfollow(request):
    try:
        if 'username' in request.data:
            user: User = User.objects.get(username=request.data['username'])
        else:
            return Response({'error': 'نام کاربری وارد نشده است.'}, status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'error': 'نام کاربری وارد شده صحیح نیست.'}, status.HTTP_404_NOT_FOUND)

    user.profile.followers.remove(request.user)
    return Response({}, status.HTTP_200_OK)


@api_view(['POST'])
def edit_profile(request):
    serializer = EditUserInfoSerializer(data=request.data)
    if serializer.is_valid():
        if 'username' in serializer.validated_data:
            username = serializer.validated_data['username']
            if User.objects.filter(username=username):
                return Response({'error': 'نام کاربری تکراری است.'}, status.HTTP_409_CONFLICT)
            request.user.username = username
        if 'first_name' in serializer.validated_data:
            request.user.first_name = serializer.validated_data['first_name']
        if 'notif_enabled' in serializer.validated_data['profile']:
            request.user.profile.notif_enabled = serializer.validated_data[
                'profile']['notif_enabled']
        request.user.save()
        return Response({}, status.HTTP_200_OK)
    return Response({'error': serializer.error_messages}, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_photo(request):
    serializer = ChangePhotoSerializer(data=request.data)
    if serializer.is_valid():
        print(serializer.validated_data)
        if request.user.profile.photo:
            prev_photo = request.user.profile.photo.path
            os.remove(prev_photo)
            request.user.profile.photo.delete()
        if serializer.validated_data:
            request.user.profile.photo = serializer.validated_data['profile']['photo']
        request.user.save()
        return Response({}, status.HTTP_200_OK)
    return Response({'error': serializer.error_messages}, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('username', openapi.IN_QUERY,
                          description="Username of the user", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Response(description='User brief retrieved successfully', schema=ShortProfileSerializer),
        404: openapi.Response(description='User not found', examples={"application/json": {"error": "User not found."}})
    },
    operation_description="Get a brief profile of a user. If no username is provided, the profile of the current user is returned."
)
@api_view(['GET'])
def get_user_brief(request):
    username = request.GET.get('username')
    if username:
        user: User = User.objects.get(username=username)
    else:
        user: User = request.user
    serializer = ShortProfileSerializer(user)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
def search_users(request):
    username = request.GET.get('username')
    if username:
        user: User = User.objects.filter(username__icontains=username)
    else:
        user: User = request.user
    serializer = UserSerializer(user, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
def get_new_badges(request):
    user: User = request.user
    user_badges = UserBadge.objects.filter(profile=user.profile, is_new=True)
    for ub in user_badges:
        ub.is_new = False
        ub.save()
    return Response(UserBadgeSerializer(instance=user_badges, many=True).data, status.HTTP_200_OK)


@api_view(['GET'])
def statistics(request):
    user: User = request.user
    response = []

    today = timezone.now().date()
    for i in range(7):
        _date = today - timedelta(days=i)
        res = {'date': _date.isoformat()}

        # Habits
        weekday = (_date.weekday() + 2) % 7

        # Passed Repeated Habits
        passed_habit_instances = HabitInstance.objects.filter(habit__user=request.user, habit__is_repeated=True,
                                                              habit__start_date__lte=_date, habit__modify_date__gt=_date, due_date=_date)

        # Repeated Habits
        repeated_habits = Habit.objects.filter(Q(user=request.user), Q(is_repeated=True), Q(modify_date__lte=_date), Q(
            due_date=None) | Q(due_date__gte=_date)).filter(repeated_days__regex='^\d{'+str(weekday)+'}1\d{'+str(6-weekday)+'}$')

        # Non-Repeated Habits
        non_repeated_habits = Habit.objects.filter(
            user=request.user, is_repeated=False, due_date=_date)

        habits = repeated_habits.union(non_repeated_habits)
        instances = []
        for h in habits:
            hi, _ = HabitInstance.objects.get_or_create(
                habit=h, due_date=_date)
            instances.append(hi)

        for hi in passed_habit_instances:
            if hi.habit not in habits:
                instances.append(hi)

        instances_id = [hi.id for hi in instances]

        total_habits = 0
        completed_habits = 0

        for hi in instances:
            total_habits += 1
            if hi.is_completed:
                completed_habits += 1

        res['total_habits'] = total_habits
        res['completed_habits'] = completed_habits

        # Tracks
        t = Track.objects.filter(user=user, start_datetime__date=_date).aggregate(
            duration=Sum(F('end_datetime') - F('start_datetime')))['duration']

        total_track_duration = t.seconds if t is not None else 0
        res['total_track_duration'] = total_track_duration

        # Score
        s = Score.objects.filter(user=user, date=_date, type__in=['Habit', 'Challenge Reward']).aggregate(
            total_score=Sum('score'))
        total_score = s['total_score']
        if total_score is None:
            total_score = 0
        res['total_score'] = total_score

        # Tag-based stats
        tag_based_habits = HabitInstance.objects.filter(id__in=instances_id).values(
            'habit__tag', 'is_completed').annotate(count=Count('id'))

        habit_stats = list()
        for item in tag_based_habits:
            if not item['is_completed']:
                continue
            tag_id = item['habit__tag']
            if tag_id:
                tag = Tag.objects.get(id=tag_id)
            else:
                tag = None
            habit_stats.append({
                'tag': TagSerializer(instance=tag).data if tag is not None else None,
                'completed_habits': item['count']
            })
        res['habits'] = habit_stats

        tag_based_tracks = Track.objects.filter(user=user, start_datetime__date=_date).values('tag').annotate(
            duration=Sum(F('end_datetime') - F('start_datetime')))

        track_stats = list()
        for item in tag_based_tracks:
            tag_id = item['tag']
            if tag_id:
                tag = Tag.objects.get(id=tag_id)
            else:
                tag = None
            track_stats.append({
                'tag': TagSerializer(instance=tag).data if tag is not None else None,
                'total_track_duration': item['duration'].seconds
            })
        res['tracks'] = track_stats
        response.append(res)

    return Response(response, status.HTTP_200_OK)
