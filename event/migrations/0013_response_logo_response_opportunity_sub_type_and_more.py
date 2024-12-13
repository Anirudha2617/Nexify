# Generated by Django 5.1.2 on 2024-12-06 08:24

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0012_notification_event_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/'),
        ),
        migrations.AddField(
            model_name='response',
            name='opportunity_sub_type',
            field=models.CharField(blank=True, choices=[], max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='response',
            name='opportunity_type',
            field=models.CharField(choices=[('General and case competition', 'General and case competition'), ('Quizzes', 'Quizzes'), ('Hackathon and coding challenge', 'Hackathon and coding challenge'), ('Scolarships', 'Scolarships'), ('Workshop and webinars', 'Workshop and webinars'), ('Conferences', 'Conferences'), ('Creative and cultural events', 'Creative and cultural events')], default='General and case competition', max_length=35),
        ),
        migrations.AlterField(
            model_name='registration_details',
            name='registration_start',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 6, 13, 54, 45, 808099)),
        ),
        migrations.AlterField(
            model_name='response',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='event.form'),
        ),
    ]