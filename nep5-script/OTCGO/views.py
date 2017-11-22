from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
import json


def index(request):
    return render_to_response('OTCGO/index.html')
