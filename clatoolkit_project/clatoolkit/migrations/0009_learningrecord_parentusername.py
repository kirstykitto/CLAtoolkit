# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0008_auto_20150904_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningrecord',
            name='parentusername',
            field=models.CharField(max_length=5000, blank=True),
        ),
    ]
