# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clatoolkit', '0015_learningrecord_parentdisplayname'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_code', models.CharField(max_length=5000)),
                ('groupId', models.IntegerField(max_length=5000)),
                ('userId', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
