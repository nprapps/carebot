#!/usr/bin/env python

from collections import OrderedDict
import json

from clan.utils import GLOBAL_ARGUMENTS
from django.shortcuts import render
from django.template.defaulttags import register

from reports.models import Project, Report

@register.filter
def get(dictionary, key):
    return dictionary.get(key)

def index(request):
    context = {
        'projects': Project.objects.all()    
    }

    return render(request, 'index.html', context)

def project(request, slug):
    obj = Project.objects.get(slug=slug)

    context = {
        'project': obj, 
        'reports': obj.reports.exclude(last_run__isnull=True)
    }

    return render(request, 'project.html', context)

def report(request, slug, ndays):
    obj = Report.objects.get(
        project__slug=slug,
        ndays=ndays
    )

    data = json.loads(obj.results_json)

    global_args = OrderedDict()

    for arg in GLOBAL_ARGUMENTS:
        if data[arg] is not None:
            global_args[arg] = data[arg]

    context = {
        'global_args': global_args,
        'report': obj 
    }

    return render(request, 'report.html', context)
