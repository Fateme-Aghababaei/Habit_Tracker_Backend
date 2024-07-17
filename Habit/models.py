from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, related_name='tags', on_delete=models.CASCADE)
    color = models.CharField(max_length=7)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'user'], name='unique_tag_user')
        ]


class Habit(models.Model):
    user = models.ForeignKey(User, related_name='habits', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField()
    tag = models.ForeignKey(Tag, null=True, on_delete=models.SET_NULL)
    start_date = models.DateField()
    due_date = models.DateField()
    is_repeated = models.BooleanField()
    repeated_days = models.CharField(max_length=7)
    score = 1

class HabitInstance(models.Model):
    habit = models.ForeignKey(Habit, related_name='instances', on_delete=models.CASCADE)
    completed_date = models.DateTimeField(null=True, blank=True)

class Track(models.Model):
    name = models.CharField(max_length=250)
    tag = models.ForeignKey(Tag, null=True, on_delete=models.SET_NULL)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)