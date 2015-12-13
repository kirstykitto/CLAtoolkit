# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0002_auto_20151123_0258'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='cl_feature',
            field=models.BooleanField(default=False),
        ),
    ]
