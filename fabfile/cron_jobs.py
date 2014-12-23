#!/usr/bin/env python

"""
Cron jobs
"""
import boto
import boto.ses
from fabric.api import local, require, task

import app_config
from reports.models import Project
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

    updated_reports = []

    for project in Project.objects.all():
        print 'Running reports for %s' % project.title
        updated_reports.extend(project.run_reports(overwrite=overwrite))
        print 'Updating social counts'
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
                app_config.S3_BUCKET['region']
            )

            ses.send_email(
                app_config.EMAIL_SEND_ADDRESS,
                'Carebot cares!',
                email_body,
                [app_config.EMAIL_NOTIFY_ADDRESS]
            )

