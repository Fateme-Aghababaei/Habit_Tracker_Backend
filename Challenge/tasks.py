from celery import shared_task
from .models import Challenge
from Habit.models import Habit, HabitInstance
from Profile.models import Score
from Notification.models import Notification


@shared_task
def challenge_rewards(id):
    challenge = Challenge.objects.get(id=id)
    for user in challenge.participants.all():
        habits = challenge.participants_habits.filter(
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

            Notification.objects.create(
                user=user, title='پایان چالش', description=f'{challenge.name} به پایان رسید. شما از این چالش {challenge.score} امتیاز گرفتید.')
            # TODO Badges
        else:
            Notification.objects.create(
                user=user, title='پایان چالش', description=f'{challenge.name} به پایان رسید. متاسفانه شما تمام عادت‌های این چالش را انجام نداده‌اید و جایزه این چالش را دریافت نمی‌کنید.')
