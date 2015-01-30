import os

from django.utils.timezone import now as timezone_now
from django.db import models

from .mixins import TimeStampedModel


def gen_filename(instance, filename):
    now = timezone_now()
    filename_base, filename_ext = os.path.splitext(filename)
    return 'uploads/%s/%s%s' % (
        str(instance.id),
        now.strftime('%Y%m%d%H%M%S%s'),
        filename_ext.lower(),
    )


class Media(TimeStampedModel):
    title = models.CharField(max_length='255', default='', blank=True)
    description = models.CharField(max_length='500', default='', blank=True)
    item = models.FileField(
        upload_to=gen_filename,
        blank=True,
        null=True
    )
