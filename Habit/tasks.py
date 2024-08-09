from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import date, timedelta, datetime
from Habit.models import Habit, HabitInstance
from django.db.models import Q

logger = get_task_logger(__name__)


@shared_task
def create_habit_instances():
    yesterday = date().today() - timedelta(days=1)
    weekday = (yesterday.weekday() + 2) % 7

    # Non-Repeated Habits
    non_repeated_habits = Habit.objects.filter(
        is_repeated=False, due_date=yesterday)

    # Repeated Habits
    repeated_habits = Habit.objects.filter(Q(is_repeated=True), Q(modify_date__lte=yesterday), Q(due_date=None) | Q(
        due_date__gte=yesterday), Q(repeated_days__regex=r'^\d{'+str(weekday)+'}1\d{'+str(6-weekday)+'}$'))

    habits = non_repeated_habits.union(repeated_habits)

    instances_created = 0
    instances_exists = 0
    for habit in habits:
        _, created = HabitInstance.objects.get_or_create(
            habit=habit, due_date=yesterday)
        if created:
            instances_created += 1
        else:
            instances_exists += 1

    logger.info(f"{instances_created} instance(s) Created. {instances_exists} instance(s) already exists. Task completed at {datetime.now().isoformat()}.")
