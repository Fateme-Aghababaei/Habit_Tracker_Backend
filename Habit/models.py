from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, related_name='tags',
                             on_delete=models.CASCADE)
    color = models.CharField(max_length=10)

    def __str__(self):
        return f'[User: {str(self.user)}] {self.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'user'], name='unique_tag_user')
        ]


class Habit(models.Model):
    user = models.ForeignKey(
        User, related_name='habits', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    tag = models.ForeignKey(Tag, null=True, blank=True,
                            on_delete=models.SET_NULL)
    start_date = models.DateField(auto_now_add=True)
    modify_date = models.DateField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    is_repeated = models.BooleanField()
    repeated_days = models.CharField(max_length=7, null=True, blank=True)
    score = 1
    from_challenge = models.ForeignKey(
        to='Challenge.Challenge', on_delete=models.CASCADE, related_name='participants_habits', null=True, blank=True)

    def __str__(self):
        return f'[User: {str(self.user)}] {self.name}'


class HabitInstance(models.Model):
    habit = models.ForeignKey(
        Habit, related_name='instances', on_delete=models.CASCADE)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.due_date} - {self.habit}'
