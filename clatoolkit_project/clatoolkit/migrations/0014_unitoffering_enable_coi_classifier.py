# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0013_auto_20151028_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitoffering',
            name='enable_coi_classifier',
            field=models.BooleanField(default=False),
        ),
    ]
