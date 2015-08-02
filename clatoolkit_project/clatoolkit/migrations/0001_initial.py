# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardReflection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=5000)),
                ('strategy', models.TextField()),
                ('rating', models.CharField(default=b'Satisfied', max_length=50, choices=[(b'Happy', b'Happy'), (b'Satisfied', b'Satisfied'), (b'Unhappy', b'Unhappy')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LearningRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('xapi', django_pgjson.fields.JsonField()),
                ('course_code', models.CharField(max_length=5000)),
                ('platform', models.CharField(max_length=5000)),
                ('verb', models.CharField(max_length=5000)),
                ('username', models.CharField(max_length=5000, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnitOffering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=5000)),
                ('name', models.CharField(max_length=5000)),
                ('semester', models.CharField(max_length=5000)),
                ('description', models.TextField()),
                ('twitter_hashtags', models.TextField()),
                ('google_groups', models.TextField()),
                ('facebook_groups', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('users', models.ManyToManyField(related_name='usersinunitoffering', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fb_id', models.CharField(max_length=30)),
                ('twitter_id', models.CharField(max_length=30)),
                ('ll_endpoint', models.CharField(max_length=60)),
                ('ll_username', models.CharField(max_length=60)),
                ('ll_password', models.CharField(max_length=60)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
