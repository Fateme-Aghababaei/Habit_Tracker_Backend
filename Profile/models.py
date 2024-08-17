from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from Badge.models import Badge


def generate_code():
    return get_random_string(10)


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    inviter = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='invited_users', null=True, blank=True)
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    score = models.IntegerField(default=0)
    streak_start = models.DateField(null=True, blank=True)
    streak_end = models.DateField(null=True, blank=True)
    followers = models.ManyToManyField(
        User, related_name='followings', blank=True)
    notif_enabled = models.BooleanField(null=True, blank=True)
    badges = models.ManyToManyField(Badge, through='UserBadge', blank=True)
    completed_habits = models.IntegerField(default=0)
    completed_challenges = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    p, c = Profile.objects.get_or_create(user=instance)
    instance.profile.save()


class Score(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='score_history')
    date = models.DateField(auto_now_add=True)
    score = models.IntegerField()
    type = models.CharField(max_length=20)

    def __str__(self):
        return f'[User: {self.user}] - [Type: {self.type}]'


class UserBadge(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    is_new = models.BooleanField(default=True)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[User: {self.profile.user}] - [Badge: {self.badge}]'
