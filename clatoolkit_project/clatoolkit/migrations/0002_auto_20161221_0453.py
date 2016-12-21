# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningrecord',
            name='xapi',
        ),
        migrations.AddField(
            model_name='learningrecord',
            name='statement_id',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='learningrecord',
            name='platform',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='learningrecord',
            name='verb',
            field=models.CharField(max_length=50),
        ),
    ]
