from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import date, timedelta, datetime
from django.utils import timezone
from Habit.models import Habit, HabitInstance
from django.db.models import Q
from django.contrib.auth.models import User
from .models import HabitInstance
from Badge.models import Badge
from Profile.models import UserBadge
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = get_task_logger(__name__)


@shared_task
def create_habit_instances(_from: date = None, _to: date = None):
    if _from is None and _to is None:
        _from = timezone.now().date() - timedelta(days=1)
        _to = _from

    d = _from
    while d <= _to:
        weekday = (d.weekday() + 2) % 7

        # Non-Repeated Habits
        non_repeated_habits = Habit.objects.filter(
            is_repeated=False, due_date=d)

        # Repeated Habits
        repeated_habits = Habit.objects.filter(Q(is_repeated=True), Q(modify_date__lte=d), Q(due_date=None) | Q(
            due_date__gte=d), Q(repeated_days__regex=r'^\d{'+str(weekday)+'}1\d{'+str(6-weekday)+'}$'))

        habits = non_repeated_habits.union(repeated_habits)

        instances_created = 0
        instances_exists = 0
        for habit in habits:
            _, created = HabitInstance.objects.get_or_create(
                habit=habit, due_date=d)
            if created:
                instances_created += 1
            else:
                instances_exists += 1

        logger.info(
            f"for [{d.isoformat()}]: {instances_created} instance(s) Created. {instances_exists} instance(s) already exists. Task completed at {timezone.now().isoformat()}.")
        d = d + timedelta(days=1)


@shared_task
def check_for_habit_badges(user: User):
    has_new_badges = False

    completed_habits = user.profile.completed_habits
    eligible_badges = Badge.objects.filter(
        type='habit', count__lte=completed_habits)

    for badge in eligible_badges:
        if badge not in user.profile.badges.all():
            UserBadge.objects.create(profile=user.profile, badge=badge)
            has_new_badges = True

    return has_new_badges


@shared_task
def habit_reminder_email():
    for user in User.objects.all():
        habit_date = timezone.now().date()
        weekday = (habit_date.weekday() + 2) % 7

        # Passed Repeated Habits
        passed_habit_instances = HabitInstance.objects.filter(habit__user=user, habit__is_repeated=True,
                                                            habit__start_date__lte=habit_date, habit__modify_date__gt=habit_date, due_date=habit_date)

        # Repeated Habits
        repeated_habits = Habit.objects.filter(Q(user=user), Q(is_repeated=True), Q(modify_date__lte=habit_date), Q(
            due_date=None) | Q(due_date__gte=habit_date)).filter(repeated_days__regex='^\d{'+str(weekday)+'}1\d{'+str(6-weekday)+'}$')

        # Non-Repeated Habits
        non_repeated_habits = Habit.objects.filter(
            user=user, is_repeated=False, due_date=habit_date)

        habits = repeated_habits.union(non_repeated_habits)
        instances = []
        for h in habits:
            hi, _ = HabitInstance.objects.get_or_create(
                habit=h, due_date=habit_date)
            instances.append(hi)

        for hi in passed_habit_instances:
            if hi.habit not in habits:
                instances.append(hi)

        incomplete_habits = 0

        for instance in instances:
            if not instance.is_completed:
                incomplete_habits += 1
        
        if incomplete_habits > 0:
            try:
                email_body = render_to_string('Habit/reminder_email.html', {'count': incomplete_habits})
                subject = 'کارات | یادآوری انجام عادت'
                email = EmailMessage(subject=subject, body=email_body, to=[user.email])
                email.content_subtype = 'html'
                email.send()
            except Exception as e:
                print(e)