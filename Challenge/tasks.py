from celery import shared_task
from .models import Challenge
from Habit.models import Habit, HabitInstance
from Profile.models import Score
from django.db.models import BaseManager


@shared_task
def challenge_rewards(id):
    challenge = Challenge.objects.get(id=id)
    for user in challenge.participants.all():
        habits: BaseManager[Habit] = challenge.participants_habits.filter(
            user=user)
        instances = HabitInstance.objects.filter(habit__in=habits)
        all_instances = instances.count()
        completed_instances = instances.filter(is_completed=True).count()

        # Rewards
        if completed_instances == all_instances:
            user.profile.score += challenge.score
            user.save()
            Score.objects.create(
                user=user, score=challenge.score, type='Challenge Reward')

            # TODO Notif
            # TODO Badges
