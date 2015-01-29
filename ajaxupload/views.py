import json
from django.utils.timezone import now as timezone_now

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
            print(request.META['HTTP_CONTENT_DISPOSITION'])
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