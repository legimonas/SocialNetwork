# Generated by Django 2.2.4 on 2020-01-28 18:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20200128_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='receiving_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 28, 21, 42, 26, 293965)),
        ),
    ]
