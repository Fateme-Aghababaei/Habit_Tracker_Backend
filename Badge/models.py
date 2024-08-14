from django.db import models
from django.contrib.auth.models import User


class Badge(models.Model):
    TYPES = [
        ('streak', 'Streak'), ('habit', 'Habit'), ('challenge', 'Challenge'),
    ]
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    image = models.ImageField(upload_to='badges/')
    type = models.CharField(max_length=20, choices=TYPES)
    count = models.IntegerField()
