from django.db import models
from django.contrib.auth.models import User
from Habit.models import Habit
from django.utils.crypto import get_random_string


def generate_code():
    print("111111111111111")
    while True:
        print("22222222222222")
        code = get_random_string(10)
        if Challenge.objects.filter(share_code=code):
            print("3333333333333")
            continue
        else:
            print("444444444444")
            break
    print("5555555555")
    return code


class Challenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    photo = models.ImageField(upload_to='challenges/', null=True, blank=True)
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='challenges_created')
    participants = models.ManyToManyField(User, related_name="challenges")
    start_date = models.DateField()
    end_date = models.DateField()
    habits = models.ManyToManyField(Habit)
    score = models.PositiveSmallIntegerField(default=50)
    price = models.PositiveSmallIntegerField(default=0)
    share_code = models.CharField(
        max_length=10, default=generate_code, unique=True)
