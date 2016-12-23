# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0003_learningrecord_xapi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oauthflowtemp',
            name='course_code',
        ),
        migrations.AddField(
            model_name='oauthflowtemp',
            name='unit',
            field=models.ForeignKey(default=1, to='clatoolkit.UnitOffering'),
            preserve_default=False,
        ),
    ]
