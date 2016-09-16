# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0014_unitoffering_enable_coi_classifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningrecord',
            name='parentdisplayname',
            field=models.CharField(max_length=5000, blank=True),
        ),
    ]
