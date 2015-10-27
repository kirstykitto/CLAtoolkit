# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0011_cachedcontent'),
    ]

    operations = [
        migrations.AddField(
            model_name='cachedcontent',
            name='activitytable',
            field=models.TextField(blank=True),
        ),
    ]
