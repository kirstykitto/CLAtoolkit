# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clatoolkit', '0010_auto_20151006_0409'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.CharField(max_length=1000)),
                ('classifier', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('xapistatement', models.ForeignKey(to='clatoolkit.LearningRecord')),
            ],
        ),
        migrations.CreateModel(
            name='UserClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=5000)),
                ('isclassificationcorrect', models.BooleanField()),
                ('userreclassification', models.CharField(max_length=1000)),
                ('feedback', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('classification', models.ForeignKey(to='clatoolkit.Classification')),
            ],
        ),
    ]
