# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.CharField(max_length=5000)),
                ('credentials_json', django_pgjson.fields.JsonField()),
            ],
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='ll_endpoint',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='ll_password',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='ll_username',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(default=b'Student', max_length=100, choices=[(b'Staff', b'Staff'), (b'Student', b'Student')]),
        ),
    ]
