# Generated by Django 5.0.7 on 2024-07-28 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0005_alter_profile_notification_enabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='notification_enabled',
        ),
        migrations.AddField(
            model_name='profile',
            name='notif_enabled',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
