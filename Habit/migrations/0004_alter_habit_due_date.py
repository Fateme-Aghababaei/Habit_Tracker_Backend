# Generated by Django 5.0.7 on 2024-07-30 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Habit', '0003_alter_habit_repeated_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
