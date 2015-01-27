from django.db import models

from .mixins import TimeStampedModel


class Media(TimeStampedModel):
    title = models.CharField(max_length='255', default='')
    description = models.CharField(max_length='500', default='')
    item = models.FileField(upload_to='uploads/')