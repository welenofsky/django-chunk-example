# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajaxupload', '0002_auto_20150130_2036'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='upload_id',
            field=models.CharField(default='', blank=True, max_length='32'),
            preserve_default=True,
        ),
    ]
