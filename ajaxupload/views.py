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
        ChunkInfo = get_file_info(request.POST, request.META)
        f = request.FILES['item']
        if ChunkInfo and int(ChunkInfo["CHUNK_START"]) == 0:
            """ Handle first chunk """
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

            print(ChunkInfo['FILENAME'])
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
            instance = Media.objects.get(upload_id=ChunkInfo['UPLOAD_ID'])
            file = {
                "name": instance.item.url,
                "size": ChunkInfo['CHUNK_TOTAL'],
                "upload_id": ChunkInfo['UPLOAD_ID']
            }
            data['files'].append(file)
            handle_uploaded_chunk(f, ChunkInfo)
    else:
        """ Not Chunky """
        print(request.FILES['item'].name)
        form = MediaForm(request.POST, request.FILES)

        if form.is_valid():
            instance = Media(
                item=request.FILES['item'],
                upload_id=request.POST['upload_id']
            )
            instance.save()
            file = {
                "name": instance.item.name,
                "size": request.META['CONTENT_LENGTH']
            }
            data['files'].append(file)
    print("\n\nDUMPING\n\n%s\n" % json.dumps(data))
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


def handle_uploaded_chunk(f, chunk_info):
    try:
        if len(chunk_info['UPLOAD_ID'].rstrip()) == 32:
            media_obj = Media.objects.get(upload_id=chunk_info['UPLOAD_ID'])
            chunk_save_location = media_obj.item.url
            with storage.open(chunk_save_location, 'ab') as destination:
                destination.write(f.read())
    except Exception as e:
        print("Exception met when handling chunk: %s" % e)


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


def get_file_info(request_post, request_meta):
    # Init variables
    upload_id = ''
    original_filename = ''
    FileInfo = ''

    if 'HTTP_CONTENT_DISPOSITION' in request_meta:
        """ Chunky """
        cs_results = ''
        # Fill variables
        original_filename = re.findall(
            'filename="(.*?)"',
            request_meta['HTTP_CONTENT_DISPOSITION'])[0]
        # CSR: Chunk size regex
        csr = re.compile(r'\d+')
        cs_results = csr.findall(request_meta['HTTP_CONTENT_RANGE'])

        if ('upload_id' in request_post and
                len(request_post['upload_id']) == 32):
            upload_id = request_post['upload_id']

        if len(cs_results) == 3:
            FileInfo = {
                "FILENAME": original_filename,
                "CHUNK_START": cs_results[0],
                "CHUNK_END": cs_results[1],
                "CHUNK_TOTAL": cs_results[2],
                "UPLOAD_ID": upload_id,
            }
        else:
            return('incorrect chunk sizes returned %s' % len(cs_results))

    else:
        original_filename = re.findall(
            'filename="(.*?)"',
            request_meta['HTTP_CONTENT_DISPOSITION'])[0]
        FileInfo = {
            "FILENAME": request_meta,
            "SIZE": request_meta['CONTENT_LENGTH'],

        }

    return FileInfo
