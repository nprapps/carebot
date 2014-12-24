#!/usr/bin/env python

from collections import OrderedDict
import json

from clan.utils import GLOBAL_ARGUMENTS
from django.shortcuts import render
from django.template.defaulttags import register

from reports import models

@register.filter
def get(dictionary, key):
    return dictionary.get(key)

def index(request):
    """
    Project index.
    """
    context = {
        'projects': models.Project.objects.all()    
    }

    return render(request, 'index.html', context)

def project(request, slug):
    """
    Project report index.
    """
    obj = models.Project.objects.get(slug=slug)

    context = {
        'project': obj, 
        'reports': obj.reports.exclude(last_run__isnull=True)
    }

    return render(request, 'project.html', context)

def report(request, slug, ndays):
    """
    Generate a project report.
    """
    obj = models.Report.objects.get(
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

def compare(request, slug, ndays):
    """
    Compare results of a query.
    """
    query = models.Query.objects.get(slug=slug)
    query_results = models.QueryResult.objects.filter(
        query=query,
        report__ndays=ndays
    )

    context = {
        'query': query,
        'ndays': ndays,
        'query_results': query_results
    }

    return render(request, 'query.html', context)
