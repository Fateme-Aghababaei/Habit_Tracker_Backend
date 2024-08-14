from celery import shared_task
from .models import Challenge
from Habit.models import Habit, HabitInstance
from Profile.models import Score, UserBadge
from Notification.models import Notification
from Badge.models import Badge


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
            user.profile.completed_challenges += 1
            user.save()
            Score.objects.create(
                user=user, score=challenge.score, type='Challenge Reward')

            Notification.objects.create(
                user=user, title='پایان چالش', description=f'{challenge.name} به پایان رسید. شما از این چالش {challenge.score} امتیاز گرفتید.')

            completed_challenges = user.profile.completed_challenges
            eligible_badges = Badge.objects.filter(
                type='challenge', count__lte=completed_challenges)

            for badge in eligible_badges:
                if badge not in user.profile.badges.all():
                    UserBadge.objects.create(profile=user.profile, badge=badge)

        else:
            Notification.objects.create(
                user=user, title='پایان چالش', description=f'{challenge.name} به پایان رسید. متاسفانه شما تمام عادت‌های این چالش را انجام نداده‌اید و جایزه این چالش را دریافت نمی‌کنید.')
