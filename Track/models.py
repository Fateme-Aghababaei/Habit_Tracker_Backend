from django.db import models
from Habit.models import Tag
from django.contrib.auth.models import User


class Track(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=250, null=True, blank=True)
    tag = models.ForeignKey(Tag, null=True, blank=True,
                            on_delete=models.SET_NULL)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
