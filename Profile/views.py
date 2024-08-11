from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from .serializers import LoginSerializer, ShortProfileSerializer, UserSerializer, FollowerFollowingSerializer, EditUserInfoSerializer, ChangePhotoSerializer, LoginResponseSerializer
from django.contrib.auth import authenticate, login as DjangoLogin, logout as DjangoLogout
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from datetime import date
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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

        try:
            if 'inviter' in serializer.validated_data:
                inviter_username = serializer.validated_data['inviter']
                inviter = User.objects.get(username=inviter_username)
        except:
            return Response({'error': 'معرف پیدا نشد.'}, status.HTTP_404_NOT_FOUND)

        user = User.objects.create_user(
            username=username, email=email, password=password)
        token, created = Token.objects.get_or_create(user=user)

        user.profile.streak_start = date.today()
        user.profile.streak_end = date.today()
        user.profile.notif_enabled = False
        user.first_name = username
        if 'inviter' in serializer.validated_data:
            user.profile.inviter = inviter

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
        user: User = User.objects.get(username=username)
    else:
        user: User = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
def update_streak(request):
    user: User = request.user
    date_diff = (date.today() - user.profile.streak_end).days
    if date_diff > 1:
        user.profile.streak_start = date.today()
        user.profile.streak_end = date.today()
        # streak = 1
        state = 'reset'
    elif date_diff == 1:
        user.profile.streak_end = date.today()
        # streak = (user.profile.streak_end - user.profile.streak_start).days + 1
        state = 'increased'
    else:
        state = 'unchanged'

    streak = (user.profile.streak_end - user.profile.streak_start).days + 1
    user.save()
    return Response({
        'streak': streak,
        'state': state
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
