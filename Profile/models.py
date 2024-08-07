from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string


def generate_code():
    return get_random_string(10)


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    inviter = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='invited_users', null=True)
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    score = models.IntegerField(default=0)
    streak_start = models.DateField(null=True, blank=True)
    streak_end = models.DateField(null=True, blank=True)
    followers = models.ManyToManyField(User, related_name='followings')
    # notification_enabled = models.BooleanField(null=True, blank=True)
    notif_enabled = models.BooleanField(null=True, blank=True)


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
