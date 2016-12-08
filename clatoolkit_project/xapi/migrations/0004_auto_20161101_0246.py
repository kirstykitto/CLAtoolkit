# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0003_clientapp_provider'),
    ]

    operations = [
        migrations.RenameField(
            model_name='oauthtemprequesttoken',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='useraccesstoken_lrs',
            old_name='user_id',
            new_name='user',
        ),
    ]
