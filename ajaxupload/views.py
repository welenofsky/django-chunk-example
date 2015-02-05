import os
import json
import re
import uuid
import io
import mimetypes

from django.utils.timezone import now as timezone_now
from django.core.files.storage import default_storage as storage
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from boto.s3.connection import S3Connection, Bucket, Key
from boto.s3.multipart import MultiPartUpload

from .forms import MediaForm
from .models import Media


def index(request):
    return render(request, 'ajaxupload/index.html', {
        "MAX_CHUNK_SIZE": settings.MAX_CHUNK_SIZE,
        "MAX_FILE_SIZE": settings.MAX_FILE_SIZE
    })


@csrf_exempt
def upload(request):
    if request.method == 'GET' or 'item' not in request.FILES:
        return HttpResponseBadRequest("Error: HTTP Status 400. Bad Request.")

    data = {}
    data['files'] = []

    if 'HTTP_CONTENT_DISPOSITION' in request.META:
        # Chunky
        f = request.FILES['item']
        ChunkInfo = get_file_info(request.POST, request.META)
        nfo = handle_uploaded_chunk(f, ChunkInfo)
        data['files'].append(nfo)

    print("\n\n%s\n%s\n%s" % (
        request.META['HTTP_CONTENT_DISPOSITION'],
        request.META['HTTP_CONTENT_RANGE'],
        request.META['CONTENT_TYPE'],
        )
    )
    print("%s\n" % json.dumps(data))
    return HttpResponse(
        json.dumps(data),
        content_type="application/json"
    )


def get_upload_id(request):
    upload_id = {
        "upload_id": str(uuid.uuid4().hex),
        "part": "1",
    }
    return HttpResponse(
        json.dumps(upload_id),
        content_type="application/json"
    )


def handle_uploaded_chunk(chunk, chunkinfo):
    s3conn = S3Connection(
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY
    )
    b = Bucket(s3conn, settings.AWS_STORAGE_BUCKET_NAME)
    k = Key(b)
    print("stop")
    chunk_diff = int(chunkinfo['CHUNK_TOTAL']) - int(chunkinfo['CHUNK_END'])
    if int(chunkinfo["CHUNK_START"]) == 0:
        name, ext = os.path.splitext(chunkinfo["FILENAME"])
        k.key = "uploads/%s%s" % (chunkinfo["UPLOAD_ID"], ext)
        print(k.key)
        content_type = mimetypes.guess_type(k.key)[0]
        mpu = b.initiate_multipart_upload(
            k.key,
            {"Content-Type": content_type},
            False,
            None,
            False,
            'public-read'
        )
        buff = io.BytesIO(chunk.read())
        buff.seek(0)
        part = int(chunkinfo["PART"])
        mpu.upload_part_from_file(buff, part)
        s3data = {
            "MPUID": mpu.id,
            "MPKN": mpu.key_name
        }
        info = {
            "name": mpu.key_name,
            "size": chunkinfo['CHUNK_TOTAL'],
            "upload_id": chunkinfo['UPLOAD_ID'],
            "part": chunkinfo['PART'],
            "mpuid": s3data["MPUID"]
        }
        print("id: %s, keyname: %s" % (mpu.id, mpu.key_name))
    elif chunk_diff > -2 and chunk_diff < 2:
        try:
            name, ext = os.path.splitext(chunkinfo["FILENAME"])
            k.key = "uploads/%s%s" % (chunkinfo["UPLOAD_ID"], ext)
            mpu = MultiPartUpload(b)
            mpu.id = chunkinfo["MPUID"]
            mpu.key_name = k.key
            buff = io.BytesIO(chunk.read())
            buff.seek(0)
            part = int(chunkinfo['PART'])
            mpu.upload_part_from_file(buff, part)
            print("finishing upload")
            xml = mpu.to_xml()
            completed_mpu = b.complete_multipart_upload(
                mpu.key_name,
                mpu.id, xml
            )
            print("DONE: %s" % completed_mpu.location)
        except Exception as e:
            print(e)
        info = {
            "name": k.key,
            "size": chunkinfo['CHUNK_TOTAL'],
            "upload_id": chunkinfo['UPLOAD_ID'],
            "part": chunkinfo['PART'],
            "mpuid": mpu.id,
            "uri": completed_mpu.location
        }
    else:
        print("you might be missing")

        name, ext = os.path.splitext(chunkinfo["FILENAME"])
        k.key = "uploads/%s%s" % (chunkinfo["UPLOAD_ID"], ext)
        mpu = MultiPartUpload(b)
        mpu.id = chunkinfo["MPUID"]
        mpu.key_name = k.key
        buff = io.BytesIO(chunk.read())
        buff.seek(0)
        part = int(chunkinfo['PART'])
        print(part)
        try:
            mpu.upload_part_from_file(buff, part)
        except Exception as e:
            print(e)

        info = {
            "name": k.key,
            "size": chunkinfo['CHUNK_TOTAL'],
            "upload_id": chunkinfo['UPLOAD_ID'],
            "part": part,
            "mpuid": mpu.id,
        }

    return info


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
    filename = 'uploads/%s%s' % (delta_time, ext.lower())
    return filename


def get_file_info(request_post, request_meta):
    # Init variables
    upload_id = ''
    original_filename = ''
    FileInfo = ''
    part = '0'
    mpuid = ''

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

        if('part' in request_post):
            part = request_post['part']

        if('mpuid' in request_post):
            mpuid = request_post['mpuid']

        if len(cs_results) == 3:
            FileInfo = {
                "FILENAME": original_filename,
                "CHUNK_START": cs_results[0],
                "CHUNK_END": cs_results[1],
                "CHUNK_TOTAL": cs_results[2],
                "UPLOAD_ID": upload_id,
                "PART": part,
                "MPUID": mpuid
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
