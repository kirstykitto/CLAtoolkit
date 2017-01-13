# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0005_remove_learningrecord_platformparentid'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningrecord',
            name='platformparentid',
            field=models.CharField(max_length=5000, blank=True),
        ),
    ]
