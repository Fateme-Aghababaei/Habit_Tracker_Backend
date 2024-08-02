from rest_framework import serializers
from .models import Tag, Habit
from django.contrib.auth.models import User


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    color = serializers.CharField(max_length=7, required=False)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']


class AddEditHabitSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    tag = serializers.IntegerField()
    due_date = serializers.DateField(required=False)
    repeated_days = serializers.CharField(required=False)

    class Meta:
        model = Habit
        fields = ['id', 'name', 'description', 'tag',
                  'due_date', 'is_repeated', 'repeated_days']


class HabitSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = Habit
        fields = ['id', 'name', 'description', 'tag', 'start_date',
                  'due_date', 'is_repeated', 'repeated_days', 'score']
