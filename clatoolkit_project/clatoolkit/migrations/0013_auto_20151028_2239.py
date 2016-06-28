# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0012_auto_20151022_0422'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitoffering',
            name='youtube_channelIds',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='google_account_name',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
