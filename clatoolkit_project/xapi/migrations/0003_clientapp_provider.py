# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0002_clientapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientapp',
            name='provider',
            field=models.CharField(default='default_lrs', unique=True, max_length=256),
            preserve_default=False,
        ),
    ]
