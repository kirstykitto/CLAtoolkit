# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0005_auto_20150828_0032'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitoffering',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
    ]
