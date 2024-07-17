from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    code = models.CharField(max_length=10, default=lambda: Profile.generate_code(), unique=True)
    inviter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='invited_users', null=True)
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    score = models.IntegerField(default=0)
    streak_start = models.DateField(null=True, blank=True)
    streak_end = models.DateField(null=True, blank=True)
    followers = models.ManyToManyField(User, related_name='followings')
    notification_enabled = models.BooleanField(default=False)

    def generate_code(self):
        return get_random_string(10)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    p, c = Profile.objects.get_or_create(user=instance)
    p.save()
