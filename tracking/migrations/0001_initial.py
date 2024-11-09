# Generated by Django 5.1.2 on 2024-11-08 18:33

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('file', models.FileField(upload_to='uploaded_files/')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('short_note', models.CharField(blank=True, max_length=200)),
                ('department', models.CharField(choices=[('Department', 'Department'), ('User', 'User')], max_length=40)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_files', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FileMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movement_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('transfer_date', models.DateTimeField(auto_now_add=True)),
                ('feedback', models.TextField(blank=True)),
                ('short_note', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Reviewed', 'Reviewed'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_files', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_files', to=settings.AUTH_USER_MODEL)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movements', to='tracking.fileupload')),
            ],
        ),
    ]