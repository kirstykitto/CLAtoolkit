# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0010_accesslog'),
    ]

    operations = [
        migrations.CreateModel(
            name='CachedContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('htmltable', models.TextField()),
                ('course_code', models.CharField(max_length=5000)),
                ('platform', models.CharField(max_length=5000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
