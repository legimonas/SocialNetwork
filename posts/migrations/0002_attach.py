# Generated by Django 2.2.4 on 2020-01-28 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attach',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='posts_attachments')),
                ('file_extension', models.CharField(max_length=10)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.Post')),
            ],
        ),
    ]
