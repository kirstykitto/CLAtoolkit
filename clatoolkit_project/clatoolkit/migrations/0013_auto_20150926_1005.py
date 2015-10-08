# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0012_cachedcontent_activitytable'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_code', models.CharField(max_length=5000)),
                ('platform', models.CharField(max_length=5000)),
                ('verb', models.CharField(max_length=5000)),
                ('fromusername', models.CharField(max_length=5000, blank=True)),
                ('tousername', models.CharField(max_length=5000, blank=True)),
                ('platformid', models.CharField(max_length=5000, blank=True)),
                ('message', models.TextField()),
                ('datetimestamp', models.DateTimeField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='learningrecord',
            name='datetimestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='learningrecord',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]
