# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0011_classification_userclassification'),
    ]

    operations = [
        migrations.AddField(
            model_name='userclassification',
            name='feature',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='userclassification',
            name='trained',
            field=models.BooleanField(default=False),
        ),
    ]
