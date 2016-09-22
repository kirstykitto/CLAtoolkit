# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clatoolkit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitoffering',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='unitoffering',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
