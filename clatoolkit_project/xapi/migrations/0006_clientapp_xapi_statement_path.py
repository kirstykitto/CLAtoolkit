# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0005_auto_20161215_0800'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientapp',
            name='xapi_statement_path',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
    ]
