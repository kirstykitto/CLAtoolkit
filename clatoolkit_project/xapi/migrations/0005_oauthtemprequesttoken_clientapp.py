# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0004_useraccesstoken_lrs_clientapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='oauthtemprequesttoken',
            name='clientapp',
            field=models.ForeignKey(default=1, to='xapi.ClientApp'),
            preserve_default=False,
        ),
    ]
