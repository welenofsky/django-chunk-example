# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ajaxupload.models


class Migration(migrations.Migration):

    dependencies = [
        ('ajaxupload', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='item',
            field=models.FileField(upload_to=ajaxupload.models.gen_filename, blank=True, null=True),
            preserve_default=True,
        ),
    ]
