# Generated by Django 5.1.2 on 2024-12-17 08:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration_details',
            name='registration_start',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 17, 13, 59, 9, 535057)),
        ),
    ]