# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0001_squashed_0002_auto_20170213_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='slack_account_name',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
