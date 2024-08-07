from rest_framework import serializers
from .models import Challenge
from Profile.serializers import ShortProfileSerializer
from Habit.serializers import HabitSerializer


class AddEditChallengeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Challenge
        fields = ['id', 'name', 'description', 'photo',
                  'is_public', 'start_date', 'end_date', 'score', 'price']


class ChallengeSerializer(serializers.ModelSerializer):
    participants = ShortProfileSerializer(many=True)
    habits = HabitSerializer(many=True)
    created_by = ShortProfileSerializer()

    class Meta:
        model = Challenge
        fields = ['id', 'name', 'description', 'photo', 'is_public', 'created_by',
                  'start_date', 'end_date', 'score', 'price', 'participants', 'habits', 'share_code']
