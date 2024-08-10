from rest_framework import serializers
from .models import Track
from Habit.serializers import TagSerializer


class AddTrackSerializer(serializers.ModelSerializer):
    tag = serializers.IntegerField(required=False)

    class Meta:
        model = Track
        fields = ['name', 'tag', 'start_datetime', 'end_datetime']


class EditTrackSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    tag = serializers.IntegerField(required=False)

    class Meta:
        model = Track
        fields = ['id', 'name', 'tag']


class TrackSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = Track
        fields = ['id', 'name', 'tag', 'start_datetime', 'end_datetime']


class FinishTrackSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Track
        fields = ['id', 'end_datetime']


class TrackListSerializer(serializers.Serializer):
    date = serializers.DateField()
    tracks = TrackSerializer(many=True)
