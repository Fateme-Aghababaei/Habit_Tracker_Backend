from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from .serializers import LoginSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from datetime import date

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        print(serializer.data)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(email=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username
            }, status.HTTP_200_OK)
        return Response({'error': 'کاربر یافت نشد.'}, status.HTTP_404_NOT_FOUND)
    return Response({'error': 'اطلاعات صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def logout(request):
    user = request.user
    Token.objects.get(user_id=user.id).delete()
    return Response({}, status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        if User.objects.filter(username=email):
            return Response({"error": "کاربری با این ایمیل وجود دارد."}, status.HTTP_409_CONFLICT)
        
        username = f'user#{get_random_string(8)}'.lower()
        while User.objects.filter(username__iexact=username):
            username = f'user#{get_random_string(8)}'.lower()

        user = User.objects.create_user(username=username, email=email, password=password)
        token, created = Token.objects.get_or_create(user=user)

        user.profile.streak_start = date.today()
        user.profile.streak_end = date.today()
        if 'inviter' in serializer.validated_data:
            inviter_username = serializer.validated_data['inviter']
            inviter = User.objects.get(username=inviter_username)
            user.profile.inviter = inviter
        user.save()
        user.profile.save()

        return Response({
            'token': token.key, 
            'username': user.username,
        })
    return Response({'error': 'اطلاعات صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)

# TODO change password view

@api_view(['GET'])
def get_user(request):
    user: User = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status.HTTP_200_OK)