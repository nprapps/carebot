#!/usr/bin/env python

"""
Cron jobs
"""
from datetime import date
import json

import boto
import boto.ses
from django.utils import timezone
from fabric.api import local, require, task
import requests

import app_config
from reports.models import Project, Report
from render_utils import render_to_string

@task
def test():
    """
    Example cron task. Note we use "local" instead of "run"
    because this will run on the server.
    """
    require('settings', provided_by=['production', 'staging'])

    local('echo $DEPLOYMENT_TARGET > /tmp/cron_test.txt')

@task
def run_reports(overwrite='false'):
    """
    Run project reports.
    """
    overwrite = (overwrite == 'true') 

    print 'Starting at %s' % timezone.now()

    updated_reports = []

    for project in Project.objects.all():
        updated_reports.extend(project.run_reports(overwrite=overwrite))
        project.social.refresh()

    if updated_reports:
        print 'Sending notification email'

        email_body = render_to_string(
            'email.txt',
            {
                'reports': updated_reports 
            },
            '/tmp/email.txt'
        )

        if app_config.DEPLOYMENT_TARGET:
            ses = boto.ses.connect_to_region(
                app_config.SES_REGION
            )

            ses.send_email(
                app_config.EMAIL_SEND_ADDRESS,
                'Carebot cares!',
                email_body,
                [app_config.EMAIL_NOTIFY_ADDRESS]
            )

GECKOBOARD_WIDGETS = {
    'projects': [{
        'title': '123621-8996005e-6ad7-4c99-8d71-326e14377926',
        'date': '77517-ffadabe0-7363-0132-9f06-22000b490a2f',
        'sessions': '123621-96934a20-e4d1-4241-b4f2-eb194397b799',
        'social': '77517-6d790ab0-7333-0132-9ead-22000b490a2f',
        'devices': '123621-7004cb03-40fc-4391-8792-d84a5c020043'
    }, {
        'title': '77517-9da9ad80-7332-0132-9eab-22000b490a2f',
        'date': '77517-3e2547e0-7364-0132-ef2d-22000b5e86d6',
        'sessions': '77517-d0351800-7332-0132-9eac-22000b490a2f',
        'social': '77517-a547fda0-7333-0132-df92-22000b51936c',
        'devices': '77517-457cf730-7338-0132-eefa-22000b5e86d6'
    }, {
        'title': '77517-1c6c2d80-7336-0132-9ec6-22000b490a2f',
        'date': '77517-41d93a50-7364-0132-dfd5-22000b51936c',
        'sessions': '77517-1e591bc0-7336-0132-eef8-22000b5e86d6',
        'social': '77517-2020a130-7336-0132-7329-22000b5391df',
        'devices': '77517-4862e280-7338-0132-df9d-22000b51936c'
    }],
    'sessions_leaderboard': '123621-0528aa9d-a700-43d0-ae59-f6ce5cf42984'
}

@task
def update_geckoboard():
    top = Project.objects.all()[:3] 

    for i, project in enumerate(top):
        widgets = GECKOBOARD_WIDGETS['projects'][i]
        all_time_report = project.all_time_report

        _geckoboard_text(
            widgets['title'],
            '<a href="http://%s%s">%s</a>' % (
                app_config.STAGING_SERVERS[0],
                project.get_absolute_url(),
                project.title
            )
        )

        _geckoboard_text(
            widgets['date'],
            '<a href="http://%s%s">%s<br />(%s)</a>' % (
                project.domain,
                project.prefix,
                project.start_date.strftime('%b. %d'),
                '%i days ago' % (date.today() - project.start_date).days
            )
        )

        _geckoboard_number(
            widgets['sessions'],
            all_time_report.sessions,
            'sessions'
        )

        _geckoboard_number(
            widgets['social'],
            float(project.social.total()) / all_time_report.sessions,
            'social interactions per session'
        )

        query_result = all_time_report.query_results.get(query__slug='sessions-by-device-category')
        sessions_metric = query_result.metrics.all()[0]
        desktop_dimension = sessions_metric.dimensions.get(name='desktop')
        mobile_dimension = sessions_metric.dimensions.get(name='mobile')
        tablet_dimension = sessions_metric.dimensions.get(name='tablet')

        _geckoboard_rag(
            widgets['devices'],
            ('Mobile', '%.1f%%' % mobile_dimension.percent_of_total),
            ('Tablet', '%.1f' % tablet_dimension.percent_of_total),
            ('Desktop', '%.1f' % desktop_dimension.percent_of_total)
        )

    top_sessions = []
    all_time_reports = Report.objects.filter(ndays__isnull=True).order_by('-sessions')[:10]

    for report in all_time_reports:
        top_sessions.append((report.project.title, report.sessions))

    _geckoboard_leaderboard(GECKOBOARD_WIDGETS['sessions_leaderboard'], top_sessions)

def _geckoboard_push(widget_key, data):
    payload = {
        'api_key': app_config.get_secrets()['GECKOBOARD_API_KEY'],
        'data': data
    }

    response = requests.post(
        'https://push.geckoboard.com/v1/send/%s' % widget_key,
        json.dumps(payload)
    )

    if response.status_code != 200:
        print 'Failed update update Geckoboard widget %s' % widget_key
        print response.content

def _geckoboard_text(widget_key, text):
    data = {
        'item': [{
            'text': text
        }]
    }

    _geckoboard_push(widget_key, data)

def _geckoboard_number(widget_key, value, label):
    data = {
        'item': [{
            'value': value,
            'text': label
        }]
    }

    _geckoboard_push(widget_key, data)

def _geckoboard_meter(widget_key, value, min_value, max_value):
    data = {
        'item': value,
        'min': {
            'value': min_value
        },
        'max': {
            'value': max_value
        }
    }

    _geckoboard_push(widget_key, data)

def _geckoboard_leaderboard(widget_key, pairs):
    data = {
        'items': []
    }

    for label, value in pairs:
        data['items'].append({
            'label': label,
            'value': value
        })

    _geckoboard_push(widget_key, data)

def _geckoboard_rag(widget_key, red_pair, orange_pair, green_pair):
    data = {
        'item': []
    }

    for label, value in [red_pair, orange_pair, green_pair]:
        data['item'].append({
            'value': value,
            'text': label
        })

    _geckoboard_push(widget_key, data)

