# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0002_clientapp_app_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientapp',
            name='reg_lrs_account_path',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
    ]
