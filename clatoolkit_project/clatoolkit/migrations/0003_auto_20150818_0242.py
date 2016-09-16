# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0002_auto_20150817_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='fb_id',
            field=models.CharField(max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='twitter_id',
            field=models.CharField(max_length=30, blank=True),
        ),
    ]
