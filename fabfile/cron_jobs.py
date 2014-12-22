#!/usr/bin/env python

"""
Cron jobs
"""
import boto
from fabric.api import local, require, task

import app_config
from reports.models import Project

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

    s3 = boto.connect_s3()

    # fake deployment target
    if not app_config.DEPLOYMENT_TARGET:
        app_config.configure_targets('staging')

    for project in Project.objects.all():
        project.run_reports(s3=s3, overwrite=overwrite)
        project.update_index(s3=s3)

    Project.update_projects_index(s3=s3)

