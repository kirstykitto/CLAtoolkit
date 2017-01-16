# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0007_learningrecord_parent_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningrecord',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]
