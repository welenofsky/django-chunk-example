import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'ajaxupload/index.html')

@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.FILES['files[]']:
        data = {}
        data['files'] = []
        fakefile = {"name": "fakefile", "size": "400MB"}
        data['files'].append(fakefile)

        """
        data: {
            result: {
                files: [
                    file {name: "hello", size: "large"}
                ]
            }
        }
        """
        return HttpResponse(
            json.dumps(data),
            content_type = "application/json"
        )