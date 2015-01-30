# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TimeStampedModel',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('timestampedmodel_ptr', models.OneToOneField(parent_link=True, serialize=False, primary_key=True, to='ajaxupload.TimeStampedModel', auto_created=True)),
                ('title', models.CharField(max_length='255', default='', blank=True)),
                ('description', models.CharField(max_length='500', default='', blank=True)),
                ('item', models.FileField(upload_to='uploads/')),
            ],
            options={
            },
            bases=('ajaxupload.timestampedmodel',),
        ),
    ]
