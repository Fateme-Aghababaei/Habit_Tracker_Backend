from typing import Any
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    help = 'Creates a PeriodicTask that runs every midnight to create habit instances.'

    def handle(self, *args: Any, **options: Any):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="30", hour="0")
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='habit_instances_creator_task',
            task='Habit.tasks.create_habit_instances'
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully Created PeriodicTask to create habit instances (id = {task.id})"))
        else:
            self.stdout.write(self.style.WARNING(
                f"Create Habit Instances Task Already Exists (id = {task.id})"))
