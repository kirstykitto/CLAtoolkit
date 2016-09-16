# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0002_auto_20151027_0056'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitoffering',
            name='enable_coi_classifier',
            field=models.BooleanField(default=False),
        ),
    ]
