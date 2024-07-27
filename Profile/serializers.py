from rest_framework import serializers
from django.contrib.auth.models import User
from Profile.models import Profile

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    inviter = serializers.CharField(required = False)

class ProfileSerializer(serializers.ModelSerializer):
    streak = serializers.SerializerMethodField('get_streak')
    inviter = serializers.SerializerMethodField('get_inviter')

    def get_streak(self, obj):
        return (obj.streak_end - obj.streak_start).days + 1
    
    def get_inviter(self, obj):
        try:
            username = User.objects.get(id=obj.inviter).username
        except:
            username = None
        return username
    class Meta:
        model = Profile
        fields = ['photo', 'score', 'streak', 'inviter']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'profile']