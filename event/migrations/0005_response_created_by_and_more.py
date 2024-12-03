# Generated by Django 5.1.2 on 2024-12-03 15:16

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_registration_details'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='registration_details',
            name='registration_start',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 3, 20, 46, 12, 71120)),
        ),
    ]
