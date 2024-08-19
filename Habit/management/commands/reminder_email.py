from typing import Any
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    help = 'Creates a PeriodicTask that runs every night to send reminder emails.'

    def handle(self, *args: Any, **options: Any):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="22")
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='reminder_email_task',
            task='Habit.tasks.habit_reminder_email'
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully Created PeriodicTask to send reminder emails (id = {task.id})"))
        else:
            self.stdout.write(self.style.WARNING(
                f"Reminder Email Task Already Exists (id = {task.id})"))
