# Generated by Django 5.0.7 on 2024-07-27 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='code',
        ),
    ]
