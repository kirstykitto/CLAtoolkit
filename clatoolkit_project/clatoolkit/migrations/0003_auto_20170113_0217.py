# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0002_auto_20170110_0935'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningrecord',
            name='datetimestamp',
        ),
        migrations.RemoveField(
            model_name='learningrecord',
            name='message',
        ),
        migrations.RemoveField(
            model_name='learningrecord',
            name='parent_user',
        ),
        migrations.RemoveField(
            model_name='learningrecord',
            name='parent_user_external',
        ),
        migrations.RemoveField(
            model_name='learningrecord',
            name='platformparentid',
        ),
        migrations.RemoveField(
            model_name='learningrecord',
            name='senttolrs',
        ),
        migrations.RemoveField(
            model_name='learningrecord',
            name='xapi',
        ),
    ]
