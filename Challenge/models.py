from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from Habit.models import Habit


def generate_code():
    while True:
        code = get_random_string(10)
        if Challenge.objects.filter(share_code=code):
            continue
        else:
            break
    return code


class Challenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    photo = models.ImageField(upload_to='challenges/', null=True, blank=True)
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='challenges_created')
    participants = models.ManyToManyField(
        User, blank=True, related_name="challenges")
    start_date = models.DateField()
    end_date = models.DateField()
    habits = models.ManyToManyField(Habit)
    score = models.PositiveSmallIntegerField(default=50)
    price = models.PositiveSmallIntegerField(default=0)
    share_code = models.CharField(
        max_length=10, default=generate_code, unique=True)
