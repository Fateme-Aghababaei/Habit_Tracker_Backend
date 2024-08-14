from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserBadge


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    inviter = serializers.CharField(required=False)


class UserSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(source='profile.photo')
    score = serializers.IntegerField(source='profile.score')
    notif_enabled = serializers.BooleanField(source='profile.notif_enabled')

    streak = serializers.SerializerMethodField('get_streak')
    inviter = serializers.SerializerMethodField('get_inviter')
    followers_num = serializers.SerializerMethodField('get_followers_num')
    followings_num = serializers.SerializerMethodField('get_followings_num')

    badges = serializers.SerializerMethodField('get_badges')

    def get_streak(self, obj):
        return (obj.profile.streak_end - obj.profile.streak_start).days + 1

    def get_inviter(self, obj):
        try:
            username = User.objects.get(id=obj.profile.inviter).username
        except:
            username = None
        return username

    def get_followers_num(self, obj):
        return obj.profile.followers.count()

    def get_followings_num(self, obj):
        return obj.followings.count()

    def get_badges(self, obj):
        badges = UserBadge.objects.filter(profile=obj.profile).order_by(
            'badge__type', 'badge__count')
        return UserBadgeSerializer(instance=badges, many=True).data

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'photo', 'score',
                  'streak', 'inviter', 'followers_num', 'followings_num', 'notif_enabled', 'badges']


class ShortProfileSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField('get_photo', allow_null=True)
    score = serializers.IntegerField(source='profile.score', allow_null=True)

    def get_photo(self, obj):
        try:
            return obj.profile.photo.url
        except:
            return None

    class Meta:
        model = User
        fields = ['first_name', 'username', 'photo', 'score']


class FollowerFollowingSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField('get_followers')
    followings = serializers.SerializerMethodField('get_followings')

    def get_followers(self, obj):
        return ShortProfileSerializer(instance=obj.profile.followers, many=True).data

    def get_followings(self, obj):
        return ShortProfileSerializer(instance=[p.user for p in obj.followings.all()], many=True).data

    class Meta:
        model = User
        fields = ['username', 'first_name', 'followers', 'followings']


class EditUserInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    notif_enabled = serializers.BooleanField(
        source='profile.notif_enabled', required=False)

    class Meta:
        model = User
        fields = ['first_name', 'username', 'notif_enabled']


class ChangePhotoSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(source='profile.photo', required=False)

    class Meta:
        model = User
        fields = ['photo']


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()


class UserBadgeSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='badge.title')
    description = serializers.CharField(source='badge.description')
    image = serializers.ImageField(source='badge.image')

    class Meta:
        model = UserBadge
        fields = ['title', 'description', 'image', 'awarded_at']
