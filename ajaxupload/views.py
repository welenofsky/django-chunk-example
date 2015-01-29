import os
import json
import re

from django.utils.timezone import now as timezone_now
#from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage as storage
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import MediaForm
from .models import Media


def index(request):
    return render(request, 'ajaxupload/index.html')


@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.FILES['item']:
        data = {}
        data['files'] = []
        if 'HTTP_CONTENT_DISPOSITION' in request.META:
            f = request.FILES['item']

            filename = re.findall(
                'filename="(.*?)"',
                request.META['HTTP_CONTENT_DISPOSITION'])[0]
            print(filename)
            handle_uploaded_file(f, filename)
            print("\nCHUNKY\n")
            print("%s\n%s\n%s\n" % (
                request.META['HTTP_CONTENT_DISPOSITION'],
                request.META['HTTP_CONTENT_RANGE'],
                request.META['CONTENT_TYPE'],
                )
            )
        else:
            print(request.FILES['item'].name)
        form = MediaForm(request.POST, request.FILES)

        if form.is_valid():
            instance = Media(item=request.FILES['item'])
            instance.save()
            file = {
                "name": instance.item.name,
                "size": request.META['CONTENT_LENGTH']
            }
            data['files'].append(file)

        return HttpResponse(
            json.dumps(data),
            content_type="application/json"
        )


def handle_uploaded_file(f, fdest):
    try:
        with storage.open('chunky/%s' % fdest, 'ab') as destination:
            destination.write(f.read())
    except Exception as e:
        print(e)
