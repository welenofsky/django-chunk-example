import os
import json
import re
import uuid

from django.utils.timezone import now as timezone_now
from django.core.files.storage import default_storage as storage
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from .forms import MediaForm
from .models import Media


def index(request):
    return render(request, 'ajaxupload/index.html')


@csrf_exempt
def upload(request):
    if request.method == 'GET' or 'item' not in request.FILES:
        return HttpResponseBadRequest("Error: HTTP Status 400. Bad Request.")

    data = {}
    data['files'] = []

    if 'HTTP_CONTENT_DISPOSITION' in request.META:
        """ Chunky """
        f = request.FILES['item']
        original_filename = re.findall(
            'filename="(.*?)"',
            request.META['HTTP_CONTENT_DISPOSITION'])[0]
        # Chunk size regex
        csr = re.compile(r'\d+')
        cs_results = csr.findall(request.META['HTTP_CONTENT_RANGE'])
        if len(cs_results) == 3:
            ChunkInfo = {
                "FILENAME": original_filename,
                "CHUNK_START": cs_results[0],
                "CHUNK_END": cs_results[1],
                "CHUNK_TOTAL": cs_results[2],
            }
        else:
            print('incorrect chunk sizes returned %s' % len(cs_results))

        if ChunkInfo and int(ChunkInfo["CHUNK_START"]) == 0:
            stuffed_form = MediaForm(request.POST, request.FILES)
            try:
                print("saving the first chunk\n")
                print("POST STUFF: %s" % request.POST['upload_id'])
                instance = stuffed_form.save()
                print("%s %s %s" % (
                    instance.id,
                    instance.item.name,
                    instance.upload_id)
                )
            except Exception as e:
                print("broke that lol: %s" % e)

            print(original_filename)
            handle_uploaded_file(f, original_filename)
            print("\nCHUNKY\n")
            file = {
                "name": instance.item.name,
                "size": ChunkInfo["CHUNK_TOTAL"],
                "upload_id": instance.upload_id,
            }
            data['files'].append(file)
            print(json.dumps(data))
            print("%s\n%s\n%s\n" % (
                request.META['HTTP_CONTENT_DISPOSITION'],
                request.META['HTTP_CONTENT_RANGE'],
                request.META['CONTENT_TYPE'],
                )
            )
        else:
            """ Handle sequential chunks """
            pass
    else:
        """ Not Chunky """
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


def get_upload_id(request):
    upload_id = {"upload_id": str(uuid.uuid4().hex)}
    return HttpResponse(
        json.dumps(upload_id),
        content_type="application/json"
    )


def handle_uploaded_file(f, fdest):
    try:
        filename = gen_filename(fdest)
        with storage.open(filename, 'ab') as destination:
            destination.write(f.read())
    except Exception as e:
        print(e)


def gen_filename(f):
    now = timezone_now()
    base, ext = os.path.splitext(f)
    delta_time = now.strftime('%Y%m%d%H%M%S%s')
    filename = 'chunky/%s%s' % (delta_time, ext.lower())
    return filename


def save_chunky_file(f):
    pass


def get_chunk_info(chunk):
    # Chunk size regex
    csr = re.compile(r'\d+')
    cs_results = csr.findall(request.META['HTTP_CONTENT_RANGE'])
    pass
