# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xapi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientApp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('i', models.CharField(max_length=256)),
                ('s', models.CharField(max_length=256)),
            ],
        ),
    ]
