from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from .serializers import LoginSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(username=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': email
            }, status.HTTP_200_OK)
        return Response({'error': 'کاربر یافت نشد.'}, status.HTTP_404_NOT_FOUND)
    return Response({'error': 'اطلاعات صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
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
        user = User.objects.create_user(username=email, email=email, password=password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key, 
            'username': email,
            'message': 'حساب کاربری با موفقیت ایجاد شد.'
        })
    return Response({'error': 'اطلاعات صحیح نمی‌باشد.'}, status.HTTP_404_NOT_FOUND)