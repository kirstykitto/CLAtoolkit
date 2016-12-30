# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientApp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider', models.CharField(unique=True, max_length=256)),
                ('app_name', models.CharField(max_length=256)),
                ('i', models.CharField(max_length=256)),
                ('s', models.CharField(max_length=256)),
                ('protocol', models.CharField(max_length=10)),
                ('domain', models.CharField(max_length=256)),
                ('port', models.CharField(max_length=6)),
                ('auth_request_path', models.CharField(max_length=256)),
                ('access_token_path', models.CharField(max_length=256)),
                ('authorization_path', models.CharField(max_length=256)),
                ('xapi_statement_path', models.CharField(max_length=256)),
                ('reg_lrs_account_path', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='OAuthTempRequestToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=256)),
                ('secret', models.CharField(max_length=256)),
                ('clientapp', models.ForeignKey(to='xapi.ClientApp')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserAccessToken_LRS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(max_length=256)),
                ('access_token_secret', models.CharField(max_length=256)),
                ('clientapp', models.ForeignKey(to='xapi.ClientApp')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
