# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0008_learningrecord_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningrecord',
            name='message',
        ),
    ]
