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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('timestampedmodel_ptr', models.OneToOneField(serialize=False, primary_key=True, to='ajaxupload.TimeStampedModel', auto_created=True, parent_link=True)),
                ('title', models.CharField(max_length='255', default='')),
                ('description', models.CharField(max_length='500', default='')),
                ('item', models.FileField(upload_to='uploads/')),
            ],
            options={
            },
            bases=('ajaxupload.timestampedmodel',),
        ),
    ]
