# Generated by Django 5.0.7 on 2024-07-28 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0004_alter_profile_notification_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='notification_enabled',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
