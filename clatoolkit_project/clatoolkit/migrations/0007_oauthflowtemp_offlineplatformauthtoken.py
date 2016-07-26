# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clatoolkit', '0006_auto_20151201_0200'),
    ]

    operations = [
        migrations.CreateModel(
            name='OauthFlowTemp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.CharField(max_length=1000)),
                ('course_code', models.CharField(max_length=1000)),
                ('transferdata', models.CharField(max_length=1000)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OfflinePlatformAuthToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=1000)),
                ('platform', models.CharField(max_length=1000)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
