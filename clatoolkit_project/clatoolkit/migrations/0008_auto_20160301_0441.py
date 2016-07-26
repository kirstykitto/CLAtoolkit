# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0007_oauthflowtemp_offlineplatformauthtoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oauthflowtemp',
            name='user',
        ),
        migrations.AddField(
            model_name='oauthflowtemp',
            name='googleid',
            field=models.CharField(default=1, max_length=1000),
            preserve_default=False,
        ),
    ]
