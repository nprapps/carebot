#!/usr/bin/env python

"""
Project-wide application configuration.

DO NOT STORE SECRETS, PASSWORDS, ETC. IN THIS FILE.
They will be exposed to users. Use environment variables instead.
See get_secrets() below for a fast way to access them.
"""

import os

"""
NAMES
"""
# Project name to be used in urls
# Use dashes, not underscores!
PROJECT_SLUG = 'carebot'

# Project name to be used in file paths
PROJECT_FILENAME = 'carebot'

# The name of the repository containing the source
REPOSITORY_NAME = 'carebot'
GITHUB_USERNAME = 'nprapps'
REPOSITORY_URL = 'git@github.com:%s/%s.git' % (GITHUB_USERNAME, REPOSITORY_NAME)
REPOSITORY_ALT_URL = None # 'git@bitbucket.org:nprapps/%s.git' % REPOSITORY_NAME'

# Project name used for assets rig
# Should stay the same, even if PROJECT_SLUG changes
ASSETS_SLUG = 'carebot'

"""
DEPLOYMENT
"""
PRODUCTION_SERVERS = ['cron.nprapps.org']
STAGING_SERVERS = ['cron-staging.nprapps.org']

# Should code be deployed to the web/cron servers?
DEPLOY_TO_SERVERS = True

SERVER_USER = 'ubuntu'
SERVER_PYTHON = 'python2.7'
SERVER_PROJECT_PATH = '/home/%s/apps/%s' % (SERVER_USER, PROJECT_FILENAME)
SERVER_REPOSITORY_PATH = '%s/repository' % SERVER_PROJECT_PATH
SERVER_VIRTUALENV_PATH = '%s/virtualenv' % SERVER_PROJECT_PATH

# Should the crontab file be installed on the servers?
# If True, DEPLOY_TO_SERVERS must also be True
DEPLOY_CRONTAB = True

# Should the service configurations be installed on the servers?
# If True, DEPLOY_TO_SERVERS must also be True
DEPLOY_SERVICES = True

UWSGI_SOCKET_PATH = '/tmp/%s.uwsgi.sock' % PROJECT_FILENAME

# Services are the server-side services we want to enable and configure.
# A three-tuple following this format:
# (service name, service deployment path, service config file extension)
SERVER_SERVICES = [
    ('app', SERVER_REPOSITORY_PATH, 'ini'),
    ('uwsgi', '/etc/init', 'conf'),
    ('nginx', '/etc/nginx/locations-enabled', 'conf'),
]

# These variables will be set at runtime. See configure_targets() below
SERVERS = []
SERVER_BASE_URL = None
SERVER_LOG_PATH = None
DEBUG = True

PROJECT_TYPES = [
    ('app', 'App'),
    ('seamus-graphic', 'Seamus Graphic'),
    ('lookatthis-post', 'Look At This Post')
]

DEFAULT_QUERIES = [
    'totals',
    'sessions-by-device-category',
    'sessions-by-browser',
    'sessions-by-referring-domain',
    'sessions-by-referring-social-network',
    'performance',
    'time-spent-on-page-by-device-category'
]

DEFAULT_EVENT_QUERIES = [
    'share-discuss-panel-opened',
    'tweet-link-clicked',
    'facebook-share-link-clicked',
    'email-link-clicked',
    'summary-copied'
]

DEFAULT_REPORT_NDAYS = [
    1,
    7,
    30
]

EMAIL_SEND_ADDRESS = 'nprapps@npr.org'
EMAIL_NOTIFY_ADDRESS = 'nprapps@npr.org'

"""
Utilities
"""
def get_secrets():
    """
    A method for accessing our secrets.
    """
    secrets = [
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_HOST',
        'POSTGRES_PORT',
        'SHAREDCOUNT_API_KEY',
        'GECKOBOARD_API_KEY'
    ]

    secrets_dict = {}

    for secret in secrets:
        name = '%s_%s' % (PROJECT_FILENAME, secret)
        secrets_dict[secret] = os.environ.get(name, None)

    return secrets_dict

def configure_targets(deployment_target):
    """
    Configure deployment targets. Abstracted so this can be
    overriden for rendering before deployment.
    """
    global SERVERS
    global SERVER_BASE_URL
    global SERVER_LOG_PATH
    global DEBUG
    global DEPLOYMENT_TARGET
    global DISQUS_SHORTNAME

    if deployment_target == 'production':
        SERVERS = PRODUCTION_SERVERS
        SERVER_BASE_URL = 'http://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DEBUG = False
    elif deployment_target == 'staging':
        SERVERS = STAGING_SERVERS
        SERVER_BASE_URL = 'http://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DEBUG = True
    else:
        SERVERS = []
        SERVER_BASE_URL = 'http://127.0.0.1:8001/%s' % PROJECT_SLUG
        SERVER_LOG_PATH = '/tmp'
        DEBUG = True

    DEPLOYMENT_TARGET = deployment_target

"""
Run automated configuration
"""
DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', None)

configure_targets(DEPLOYMENT_TARGET)
