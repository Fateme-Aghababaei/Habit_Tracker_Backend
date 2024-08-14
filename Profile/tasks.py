from celery import shared_task
from django.contrib.auth.models import User
from Badge.models import Badge
from Profile.models import UserBadge


@shared_task
def check_for_streak_badges(user: User):
    has_new_badges = False

    streak = (user.profile.streak_end - user.profile.streak_start).days + 1
    eligible_badges = Badge.objects.filter(type='streak', count__lte=streak)

    for badge in eligible_badges:
        if badge not in user.profile.badges.all():
            UserBadge.objects.create(profile=user.profile, badge=badge)
            has_new_badges = True

    return has_new_badges
