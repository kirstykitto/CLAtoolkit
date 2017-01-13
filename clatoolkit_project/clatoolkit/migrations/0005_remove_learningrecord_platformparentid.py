# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0004_learningrecord_platformparentid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningrecord',
            name='platformparentid',
        ),
    ]
