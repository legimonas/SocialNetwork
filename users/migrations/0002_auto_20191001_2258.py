# Generated by Django 2.2.4 on 2019-10-01 19:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='birth_date',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='birth_date',
            field=models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0)),
        ),
    ]
