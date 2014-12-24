#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
from glob import glob
import os
import yaml

from django.utils.text import slugify
from fabric.api import local, settings, run, sudo, task

import app_config
import servers
from reports.models import Project, Query

SERVER_POSTGRES_CMD = 'export PGPASSWORD=$carebot_POSTGRES_PASSWORD && %s --username=$carebot_POSTGRES_USER --host=$carebot_POSTGRES_HOST --port=$carebot_POSTGRES_PORT'

@task
def server_reset_db():
    """
    Reset the database on a server.
    """
    with settings(warn_only=True):
        services = ['uwsgi']
        for service in services:
            service_name = servers._get_installed_service_name(service)
            sudo('service %s stop' % service_name)

        run(SERVER_POSTGRES_CMD % ('dropdb %s' % app_config.PROJECT_SLUG))
        run(SERVER_POSTGRES_CMD % ('createdb %s' % app_config.PROJECT_SLUG))

        for service in services:
            service_name = servers._get_installed_service_name(service)
            sudo('service %s start' % service_name)

@task
def local_reset_db():
    secrets = app_config.get_secrets()

    with settings(warn_only=True):
        local('dropdb %s' % app_config.PROJECT_SLUG)
        local('echo "CREATE USER %s WITH PASSWORD \'%s\';" | psql' % (app_config.PROJECT_SLUG, secrets['POSTGRES_PASSWORD']))

    local('createdb -O %s %s' % (app_config.PROJECT_SLUG, app_config.PROJECT_SLUG))

@task
def bootstrap_db():
    local('python manage.py migrate')
    local('python manage.py loaddata data/test_user.json')

    for yaml_path in glob('data/queries/*.yaml'):
        path, filename = os.path.split(yaml_path)
        slug, ext = os.path.splitext(filename)

        with open(yaml_path, 'r') as f:
            data = yaml.load(f)

            q = Query(
                name=data['name'],
                description=data.get('description', ''),
                slug=slug,
            )

            del data['name']

            if 'description' in data:
                q.description = data['description']
                del data['description']
                
            q.clan_yaml = yaml.dump(data, indent=4)

            q.save()

    Project.objects.create(
        title='Best Songs 2014',
        slug=slugify(u'Best Songs 2014'),
        property_id='53470309',
        domain='apps.npr.org',
        prefix='/best-songs-2014/',
        start_date='2014-12-10'
    )

    Project.objects.create(
        title='Best Books 2014',
        slug=slugify(u'Best Books 2014'),
        property_id='53470309',
        domain='apps.npr.org',
        prefix='/best-books-2014/',
        start_date='2014-12-03'
    )

