# Generated by Django 5.0.7 on 2024-08-07 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Challenge', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='challenge',
            old_name='link',
            new_name='share_code',
        ),
        migrations.AlterField(
            model_name='challenge',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='challenges/'),
        ),
    ]
