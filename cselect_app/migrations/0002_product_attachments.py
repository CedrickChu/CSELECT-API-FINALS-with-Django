# Generated by Django 5.0 on 2023-12-19 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cselect_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='attachments',
            field=models.FileField(blank=True, null=True, upload_to='attachments/'),
        ),
    ]