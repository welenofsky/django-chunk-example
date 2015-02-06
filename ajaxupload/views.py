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
    else:
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
    k.key = chunkinfo["NEWNAME"]
    content_type = mimetypes.guess_type(k.key)[0]
    chunk_diff = int(chunkinfo['CHUNK_TOTAL']) - int(chunkinfo['CHUNK_END'])

    # First chunk
    if int(chunkinfo["CHUNK_START"]) == 0:
        mpu = b.initiate_multipart_upload(
            k.key,
            {"Content-Type": content_type},
            False,
            None,
            False,
            'public-read'
        )
        upload_part_from_bytesio(mpu, chunk, chunkinfo["PART"])
        s3data = {
            "MPUID": mpu.id,
            "MPKN": mpu.key_name
        }
        info = {
            "name": mpu.key_name,
            "size": chunkinfo['CHUNK_TOTAL'],
            "upload_id": chunkinfo['UPLOAD_ID'],
            "part": chunkinfo['PART'],
            "mpuid": s3data["MPUID"],
            "content_type": content_type
        }
    # Last chunk, -2 +2 byte error forgiveness
    elif chunk_diff > -2 and chunk_diff < 2:
        mpu = get_mpu(b, chunkinfo["MPUID"], k.key)
        upload_part_from_bytesio(mpu, chunk, chunkinfo["PART"])

        xml = mpu.to_xml()
        completed_mpu = b.complete_multipart_upload(
            mpu.key_name,
            mpu.id, xml
        )
        info = {
            "name": k.key,
            "size": chunkinfo['CHUNK_TOTAL'],
            "upload_id": chunkinfo['UPLOAD_ID'],
            "part": chunkinfo['PART'],
            "mpuid": mpu.id,
            "uri": completed_mpu.location,
            "content_type":  content_type
        }
    # Middle chunk
    else:
        mpu = get_mpu(b, chunkinfo["MPUID"], k.key)
        upload_part_from_bytesio(mpu, chunk, chunkinfo["PART"])

        info = {
            "name": k.key,
            "size": chunkinfo['CHUNK_TOTAL'],
            "upload_id": chunkinfo['UPLOAD_ID'],
            "part": chunkinfo['PART'],
            "mpuid": mpu.id,
            "content_type": content_type
        }

    return info


def handle_uploaded_file(f, fdest):
    try:
        filename = gen_filename(fdest)
        with storage.open(filename, 'ab') as destination:
            destination.write(f.read())
    except Exception as e:
        print(e)


def upload_part_from_bytesio(mpu, chunk, part):
    buff = io.BytesIO(chunk.read())
    buff.seek(0)
    mpu.upload_part_from_file(buff, part)


def get_mpu(bucket, id, key_name):
    try:
        mpu = MultiPartUpload(bucket)
        mpu.id = id
        mpu.key_name = key_name
        return mpu
    except:
        return None


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
        oldname, oldext = os.path.splitext(original_filename)
        # CSR: Chunk size regex
        csr = re.compile(r'\d+')
        cs_results = csr.findall(request_meta['HTTP_CONTENT_RANGE'])

        if ('upload_id' in request_post and
                len(request_post['upload_id']) == 32):
            upload_id = request_post['upload_id']
            newname = "uploads/%s%s" % (upload_id, oldext)

        if('part' in request_post):
            part = int(request_post['part'])

        if('mpuid' in request_post):
            mpuid = request_post['mpuid']

        if len(cs_results) == 3:
            FileInfo = {
                "FILENAME": original_filename,
                "NEWNAME": newname,
                "CHUNK_START": cs_results[0],
                "CHUNK_END": cs_results[1],
                "CHUNK_TOTAL": cs_results[2],
                "UPLOAD_ID": upload_id,
                "PART": part,
                "MPUID": mpuid
            }
        else:
            pass
            # return('incorrect chunk sizes returned %s' % len(cs_results))
    else:
        original_filename = re.findall(
            'filename="(.*?)"',
            request_meta['HTTP_CONTENT_DISPOSITION'])[0]
        FileInfo = {
            "FILENAME": request_meta,
            "SIZE": request_meta['CONTENT_LENGTH'],

        }

    return FileInfo
