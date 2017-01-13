# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0003_auto_20170113_0217'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningrecord',
            name='platformparentid',
            field=models.CharField(max_length=5000, blank=True),
        ),
    ]
