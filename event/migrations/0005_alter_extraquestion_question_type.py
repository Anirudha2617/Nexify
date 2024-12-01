# Generated by Django 5.1.2 on 2024-11-27 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_extradetails_extraquestion_extraresponse_extraanswer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extraquestion',
            name='question_type',
            field=models.CharField(choices=[('TEXT', 'Text'), ('SC', 'Single Choice'), ('SA', 'Short Answer'), ('LA', 'Long Answer'), ('DD', 'Dropdown'), ('DT', 'Date and Time'), ('IMG', 'Image')], default='TEXT', max_length=20),
        ),
    ]
