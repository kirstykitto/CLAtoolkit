# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0004_auto_20150825_0452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitoffering',
            name='google_groups',
            field=models.TextField(blank=True),
        ),
    ]
