#!/usr/bin/env python

from collections import OrderedDict

from django.shortcuts import render
from django.template.defaulttags import register

import app_config
from reports import models

@register.filter
def keyvalue(dict, key):
    return dict[key]

def index(request):
    """
    Project index.
    """
    projects = models.Project.objects.all()

    context = {
        'projects': projects
    }

    return render(request, 'index.html', context)

def project(request, slug):
    """
    Project report index.
    """
    obj = models.Project.objects.get(slug=slug)

    all_shares = []
    all_shares_per_session = []
    socials = models.Social.objects.all()
    
    for social in socials:
        total = social.total()

        if total:
            all_shares.append(total)
            try:
                all_shares_per_session.append(float(total) / (float(social.project.all_time_report.sessions) / 1000))
            except TypeError:
                all_shares_per_session.append('undefined')

    try:
        shares_per_session = float(obj.social.total()) / (float(obj.all_time_report.sessions) / 1000) 
    except TypeError:
        shares_per_session = 'undefined'

    context = {
        'project': obj,
        'reports': obj.reports.exclude(last_run__isnull=True),
        'all_shares': all_shares,
        'all_shares_per_session': all_shares_per_session,
        'shares_per_session': shares_per_session
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
        'queries': models.Query.objects.filter(is_comparable=True),
        'report_ndays': app_config.DEFAULT_REPORT_NDAYS,
        'tags': models.Tag.objects.all()
    }

    query_slug = request.GET.get('query', 'totals')
    ndays = request.GET.get('ndays', None)
    context['unit'] = request.GET.get('unit', 'count')
    tag_slug = request.GET.get('tag', None)

    if ndays == 'None':
        ndays = None

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

    metric_dimensions = OrderedDict()
    results = OrderedDict()

    # Build comparison table
    for qr in query_results:
        project_title = qr.project_title

        for metric in qr.metrics.all():
            m = (metric.name, metric.display_name)

            if m not in results:
                results[m] = OrderedDict()

            if metric.name not in metric_dimensions:
                if metric.name != 'total':
                    metric_dimensions[metric.name] = []

            if project_title not in results[m]:
                results[m][project_title] = {}

            for dimension in metric.dimensions.all():
                if dimension.name not in metric_dimensions[metric.name]:
                    if dimension.name != 'total':
                        metric_dimensions[metric.name].append(dimension.name)

                if dimension.name not in results[m][project_title]:
                    results[m][project_title][dimension.name] = dimension

    for metric_name in metric_dimensions:
        metric_dimensions[metric_name].append('total')

    context.update({
        'metric_dimensions': metric_dimensions,
        'results': results
    })

    return render(request, 'compare_query.html', context)
