# Generated by Django 5.0 on 2023-12-29 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cselect_app', '0002_userprofile_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images'),
        ),
    ]
