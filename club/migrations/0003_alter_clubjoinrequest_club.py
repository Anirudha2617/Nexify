# Generated by Django 5.1.2 on 2024-11-08 13:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0002_alter_clubdetails_branch_pk_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clubjoinrequest',
            name='club',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.clubdetails'),
        ),
    ]