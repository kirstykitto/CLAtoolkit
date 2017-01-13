# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clatoolkit', '0006_learningrecord_platformparentid'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningrecord',
            name='parent_user',
            field=models.ForeignKey(related_name='parent_user', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
