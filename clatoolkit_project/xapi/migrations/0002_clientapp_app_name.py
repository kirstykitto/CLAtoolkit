# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientapp',
            name='app_name',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
    ]
