# Generated by Django 5.0.7 on 2024-08-09 09:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Track', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='user',
            field=models.ForeignKey(default=10, on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
