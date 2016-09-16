# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0016_groupmap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmap',
            name='groupId',
            field=models.IntegerField(),
        ),
    ]
