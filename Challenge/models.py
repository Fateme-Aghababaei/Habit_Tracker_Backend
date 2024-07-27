from django.db import models
from django.contrib.auth.models import User
from Habit.models import Habit
from django.utils.crypto import get_random_string

def generate_link(self):
    code = get_random_string(10)
    BASE_URL = 'localhost:8000/'
    return f'{BASE_URL}challenges/{code}'

class Challenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    photo = models.ImageField(upload_to='challenges/')
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenges_created')
    participants = models.ManyToManyField(User, related_name="challenges")
    start_date = models.DateField()
    end_date = models.DateField()
    habits = models.ManyToManyField(Habit)
    score = models.PositiveSmallIntegerField(default=50)
    price = models.PositiveSmallIntegerField(default=0)
    link = models.CharField(max_length=10, default=generate_link, unique=True)


