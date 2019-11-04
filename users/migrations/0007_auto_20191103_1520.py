# Generated by Django 2.2.4 on 2019-11-03 12:20

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20191103_0903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='available_to',
            field=models.ManyToManyField(related_name='available_profiles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(default='')),
                ('receiving_time', models.DateTimeField(default=datetime.datetime(2019, 11, 3, 15, 20, 43, 512783))),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]