# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0004_auto_20161101_0246'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientapp',
            name='access_token_path',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clientapp',
            name='auth_request_path',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clientapp',
            name='authorization_path',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clientapp',
            name='domain',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clientapp',
            name='port',
            field=models.CharField(default=1, max_length=6),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clientapp',
            name='protocol',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
    ]
