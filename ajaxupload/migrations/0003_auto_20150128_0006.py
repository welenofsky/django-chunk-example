# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajaxupload', '0002_auto_20150127_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='description',
            field=models.CharField(default='', blank=True, max_length='500'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='media',
            name='title',
            field=models.CharField(default='', blank=True, max_length='255'),
            preserve_default=True,
        ),
    ]
