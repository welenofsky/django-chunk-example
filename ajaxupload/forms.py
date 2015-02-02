from django.forms import ModelForm

from .models import Media


class MediaForm(ModelForm):

    class Meta:
        model = Media
        fields = ['item', 'title', 'description', 'upload_id']
