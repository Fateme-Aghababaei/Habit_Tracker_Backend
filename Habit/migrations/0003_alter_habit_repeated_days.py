# Generated by Django 5.0.7 on 2024-07-29 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Habit', '0002_alter_habit_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='repeated_days',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
