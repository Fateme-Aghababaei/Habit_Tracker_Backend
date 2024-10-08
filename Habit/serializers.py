from rest_framework import serializers
from .models import Tag, Habit, HabitInstance
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
    tag = serializers.IntegerField(required=False)
    due_date = serializers.DateField(required=False)
    repeated_days = serializers.CharField(required=False)

    class Meta:
        model = Habit
        fields = ['id', 'name', 'description', 'tag',
                  'due_date', 'is_repeated', 'repeated_days']


class HabitSerializer(serializers.ModelSerializer):
    tag = TagSerializer()
    from_challenge = serializers.SerializerMethodField('get_challenge_id')

    def get_challenge_id(self, obj):
        return obj.from_challenge.id if obj.from_challenge else None

    class Meta:
        model = Habit
        fields = ['id', 'name', 'description', 'tag', 'start_date',
                  'due_date', 'is_repeated', 'repeated_days', 'score', 'from_challenge']


class HabitInstanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='habit.id')
    # instance_id = serializers.IntegerField(source='id')
    name = serializers.CharField(source='habit.name')
    description = serializers.CharField(source='habit.description')
    tag = TagSerializer(source='habit.tag')
    start_date = serializers.DateField(source='habit.start_date')
    is_repeated = serializers.BooleanField(source='habit.is_repeated')
    repeated_days = serializers.CharField(source='habit.repeated_days')
    score = serializers.IntegerField(source='habit.score')
    from_challenge = serializers.SerializerMethodField('get_challenge_id')

    def get_challenge_id(self, obj):
        return obj.habit.from_challenge.id if obj.habit.from_challenge else None

    class Meta:
        model = HabitInstance
        fields = ['id', 'name', 'description', 'tag', 'start_date',
                  'due_date', 'is_repeated', 'repeated_days', 'score', 'is_completed', 'completed_date', 'from_challenge']


class CompleteHabitSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='habit.id')

    class Meta:
        model = HabitInstance
        fields = ['id', 'due_date']
