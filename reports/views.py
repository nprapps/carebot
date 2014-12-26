#!/usr/bin/env python

from collections import OrderedDict

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

def report(request, slug, ndays=None):
    """
    Generate a project report.
    """
    if ndays == 'all-time':
        ndays = None

    obj = models.Report.objects.get(
        project__slug=slug,
        ndays=ndays
    )

    context = {
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
    ndays = request.GET.get('ndays', None)
    context['unit'] = request.GET.get('unit', 'count')
    tag_slug = request.GET.get('tag', None)

    if query_slug:
        context['query'] = models.Query.objects.get(slug=query_slug)

        query_results = models.QueryResult.objects.filter(
            query=context['query'],
        )

        if ndays:
            context['ndays'] = int(ndays)
            query_results = query_results.filter(report_ndays=context['ndays'])
        else:
            context['ndays'] = ndays
            query_results = query_results.filter(report_ndays__isnull=True)

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
                m = (metric.name, metric.display_name)

                if m not in results:
                    results[m] = OrderedDict([('total', [])])

                for dimension in metric.dimensions.all():
                    if dimension.name not in results[m]:
                        results[m][dimension.name] = []

                    results[m][dimension.name].append(dimension)

                results[m]['total'].append(metric.total) 

        context.update({
            'projects': projects,
            'results': results
        })

    return render(request, 'compare_query.html', context)
