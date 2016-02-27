# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0017_auto_20160216_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='classification',
            name='classifier_model',
            field=models.CharField(max_length=1000, blank=True),
        ),
        migrations.AddField(
            model_name='unitoffering',
            name='enable_group_coi_classifier',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='groupmap',
            name='groupId',
            field=models.IntegerField(max_length=5000),
        ),
    ]
