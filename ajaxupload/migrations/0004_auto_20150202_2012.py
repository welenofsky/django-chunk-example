# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ajaxupload', '0003_media_upload_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='description',
            field=models.CharField(blank=True, max_length=500, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='media',
            name='title',
            field=models.CharField(blank=True, max_length=255, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='media',
            name='upload_id',
            field=models.CharField(blank=True, max_length=32, default=''),
            preserve_default=True,
        ),
    ]
