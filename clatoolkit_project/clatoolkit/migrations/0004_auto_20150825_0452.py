# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0003_auto_20150818_0152'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitoffering',
            name='forum_urls',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='unitoffering',
            name='ll_endpoint',
            field=models.CharField(max_length=60, blank=True),
        ),
        migrations.AddField(
            model_name='unitoffering',
            name='ll_password',
            field=models.CharField(max_length=60, blank=True),
        ),
        migrations.AddField(
            model_name='unitoffering',
            name='ll_username',
            field=models.CharField(max_length=60, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='forum_id',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='unitoffering',
            name='facebook_groups',
            field=models.TextField(blank=True),
        ),
    ]
