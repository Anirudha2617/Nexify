# Generated by Django 5.1.2 on 2024-12-17 14:39

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('club', '0006_alter_clubdata_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='form_images/')),
            ],
        ),
        migrations.CreateModel(
            name='ExtraQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('question_type', models.CharField(choices=[('TEXT', 'Text'), ('SC', 'Single Choice'), ('MC', 'Multiple Choice'), ('SA', 'Short Answer'), ('LA', 'Long Answer'), ('DD', 'Dropdown'), ('DT', 'Date and Time'), ('IMG', 'Image')], default='TEXT', max_length=20)),
                ('choices', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='question_images/')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='my_forms.extradetails')),
            ],
        ),
        migrations.CreateModel(
            name='ExtraResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='my_forms.extradetails')),
            ],
        ),
        migrations.CreateModel(
            name='ExtraAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField(blank=True, null=True)),
                ('answer_image', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='my_forms.extraquestion')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='my_forms.extraresponse')),
            ],
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_type', models.CharField(default='miscillineous', max_length=40)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='form_images/')),
                ('is_public', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_forms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='extradetails',
            name='Model',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='extradetails', to='my_forms.form'),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('question_type', models.CharField(choices=[('TEXT', 'Text'), ('MC', 'Multiple Choice'), ('SA', 'Short Answer'), ('LA', 'Long Answer'), ('DD', 'Dropdown'), ('DT', 'Date and Time'), ('IMG', 'Image')], default='TEXT', max_length=20)),
                ('choices', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='question_images/')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='my_forms.form')),
            ],
        ),
        migrations.CreateModel(
            name='Registration_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibility', models.CharField(choices=[('Public', 'Public'), ('Clubs', 'Clubs'), ('Invited', 'Invited')], default='individual', max_length=20)),
                ('compulsary', models.BooleanField(default=False)),
                ('platform', models.BooleanField()),
                ('participation_type', models.CharField(choices=[('individual', 'Individual'), ('group', 'Group')], default='individual', max_length=20)),
                ('minimum_members', models.IntegerField(default=1)),
                ('maximum_members', models.IntegerField(default=1)),
                ('registration_start', models.DateTimeField(default=datetime.datetime(2024, 12, 17, 20, 9, 14, 719258))),
                ('registration_end', models.DateTimeField()),
                ('number_of_registration', models.IntegerField(blank=True, null=True)),
                ('accepted_users', models.ManyToManyField(blank=True, related_name='accepted_forms', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registration_details', to=settings.AUTH_USER_MODEL)),
                ('form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registration_details', to='my_forms.form')),
                ('invited_club', models.ManyToManyField(blank=True, related_name='forms', to='club.clubdetails')),
                ('invited_users', models.ManyToManyField(blank=True, related_name='invited_forms', to=settings.AUTH_USER_MODEL)),
                ('rejected_users', models.ManyToManyField(blank=True, related_name='rejected_forms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('success', 'Success')], default='info', max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('status', models.BooleanField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sent_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_sent_notifications', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_notifications', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='form_notifications', to='my_forms.registration_details')),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='my_forms.form')),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitted_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='registration_details',
            name='response',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registration_details', to='my_forms.response'),
        ),
        migrations.AddField(
            model_name='extraresponse',
            name='response',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='extra_responses', to='my_forms.response'),
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField(blank=True, null=True)),
                ('answer_image', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='my_forms.question')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='my_forms.response')),
            ],
        ),
    ]
