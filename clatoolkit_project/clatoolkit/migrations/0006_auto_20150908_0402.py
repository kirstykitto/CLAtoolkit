# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0005_auto_20150828_0115'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningrecord',
            name='parentusername',
            field=models.CharField(max_length=5000, blank=True),
        ),
        migrations.AddField(
            model_name='learningrecord',
            name='platformid',
            field=models.CharField(max_length=5000, blank=True),
        ),
        migrations.AddField(
            model_name='learningrecord',
            name='platformparentid',
            field=models.CharField(max_length=5000, blank=True),
        ),
        migrations.AddField(
            model_name='learningrecord',
            name='senttolrs',
            field=models.CharField(max_length=5000, blank=True),
        ),
        migrations.AddField(
            model_name='unitoffering',
            name='event',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(default=b'Student', max_length=100, choices=[(b'Staff', b'Staff'), (b'Student', b'Student'), (b'Visitor', b'Visitor')]),
        ),
    ]
