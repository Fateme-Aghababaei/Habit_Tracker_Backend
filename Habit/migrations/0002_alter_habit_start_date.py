# Generated by Django 5.0.7 on 2024-07-29 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Habit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='start_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
