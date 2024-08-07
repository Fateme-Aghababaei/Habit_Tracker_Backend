from rest_framework.decorators import api_view
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import AddEditChallengeSerializer, ChallengeSerializer
from .models import Challenge


@api_view(['POST'])
def add_challenge(request):
    serializer = AddEditChallengeSerializer(data=request.data)
    if serializer.is_valid():
        ch = serializer.save(created_by=request.user)
        return Response(ChallengeSerializer(instance=ch).data, status.HTTP_200_OK)
    return Response({'error': 'اطلاعات واردشده صحیح نمی‌باشد.'}, status.HTTP_400_BAD_REQUEST)
