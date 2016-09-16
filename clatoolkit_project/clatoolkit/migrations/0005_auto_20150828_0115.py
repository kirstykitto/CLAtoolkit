# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0004_auto_20150827_0436'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitoffering',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='unitoffering',
            name='google_groups',
            field=models.TextField(blank=True),
        ),
    ]
