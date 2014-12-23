#!/usr/bin/env python

from django.http import HttpResponse
from django.shortcuts import render

from reports.models import Project, Report

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

    return HttpResponse(obj.results_html)

