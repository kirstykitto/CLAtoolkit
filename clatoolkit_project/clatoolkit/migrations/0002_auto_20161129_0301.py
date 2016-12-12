# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0004_auto_20161101_0246'),
        ('clatoolkit', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitoffering',
            name='ll_endpoint',
        ),
        migrations.RemoveField(
            model_name='unitoffering',
            name='ll_password',
        ),
        migrations.RemoveField(
            model_name='unitoffering',
            name='ll_username',
        ),
        migrations.AddField(
            model_name='unitoffering',
            name='lrs_provider',
            field=models.ForeignKey(default=1, to='xapi.ClientApp'),
            preserve_default=False,
        ),
    ]
