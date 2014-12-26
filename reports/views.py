#!/usr/bin/env python

from collections import OrderedDict
import json

from clan.utils import GLOBAL_ARGUMENTS
from django.shortcuts import render

import app_config
from reports import models

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

def compare_query(request):
    """
    Compare results of a query.
    """
    context= {
        'queries': models.Query.objects.all(),
        'report_ndays': app_config.DEFAULT_REPORT_NDAYS,
        'tags': models.Tag.objects.all()
    }

    query_slug = request.GET.get('query', None)
    context['ndays'] = int(request.GET.get('ndays', app_config.DEFAULT_REPORT_NDAYS[0]))
    context['unit'] = request.GET.get('unit', 'count')
    tag_slug = request.GET.get('tag', None)

    if query_slug and context['ndays']:
        context['query'] = models.Query.objects.get(slug=query_slug)

        query_results = models.QueryResult.objects.filter(
            query=context['query'],
            report_ndays=context['ndays']
        )

        if tag_slug:
            context['tag'] = models.Tag.objects.get(slug=tag_slug)
            query_results = query_results.filter(
                report__project__tags=context['tag']
            )

        projects = []
        results = OrderedDict()

        # Build comparison table
        for qr in query_results:
            projects.append(qr.report.project)

            for metric in qr.metrics.all():
                if metric.name not in results:
                    results[metric.name] = OrderedDict([('total', [])])

                for dimension in metric.dimensions.all():
                    if dimension.name not in results[metric.name]:
                        results[metric.name][dimension.name] = []

                    results[metric.name][dimension.name].append(dimension)

                results[metric.name]['total'].append(metric.total) 

        context.update({
            'projects': projects,
            'results': results
        })

    return render(request, 'compare_query.html', context)
