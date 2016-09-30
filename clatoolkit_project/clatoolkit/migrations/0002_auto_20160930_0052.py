# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='learningrecord',
            old_name='unit_offering',
            new_name='unit',
        ),
    ]
