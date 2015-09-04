# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0006_unitoffering_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitoffering',
            name='event',
            field=models.BooleanField(default=False),
        ),
    ]
