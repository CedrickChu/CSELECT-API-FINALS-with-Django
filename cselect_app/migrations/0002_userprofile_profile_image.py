# Generated by Django 5.0 on 2023-12-29 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cselect_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='static/profile_images/'),
        ),
    ]