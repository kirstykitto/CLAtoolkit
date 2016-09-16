# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0005_groupmap'),
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
    ]
