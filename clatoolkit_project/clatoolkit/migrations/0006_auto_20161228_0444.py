# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clatoolkit', '0005_oauthflowtemp_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPlatformResourceMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_id', models.CharField(max_length=5000)),
                ('platform', models.CharField(max_length=100)),
                ('unit', models.ForeignKey(to='clatoolkit.UnitOffering')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='usertrellocourseboardmap',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserTrelloCourseBoardMap',
        ),
    ]
