# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lti', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ltiprofile',
            name='roles',
        ),
        migrations.AddField(
            model_name='ltiprofile',
            name='ethics_agreement',
            field=models.BooleanField(default=False),
        ),
    ]
