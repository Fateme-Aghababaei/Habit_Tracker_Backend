# Generated by Django 5.0.7 on 2024-08-09 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Habit', '0009_alter_habit_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='from_challenge',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
