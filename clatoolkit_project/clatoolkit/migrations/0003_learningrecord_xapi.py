# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0002_auto_20161221_0453'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningrecord',
            name='xapi',
            field=django_pgjson.fields.JsonField(default={}),
            preserve_default=False,
        ),
    ]
