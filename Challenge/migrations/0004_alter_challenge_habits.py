# Generated by Django 5.0.7 on 2024-08-15 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Challenge', '0003_alter_challenge_participants'),
        ('Habit', '0012_delete_track'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='habits',
            field=models.ManyToManyField(blank=True, to='Habit.habit'),
        ),
    ]
