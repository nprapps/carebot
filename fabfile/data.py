#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
from datetime import datetime
from glob import glob
import json
import yaml

import boto
from fabric.api import local, settings, run, sudo, task
from facebook import GraphAPI
from jinja2 import Template
from twitter import Twitter, OAuth

import app_config
import copytext
import flat
import public_app
import servers

SERVER_POSTGRES_CMD = 'export PGPASSWORD=$carebot_POSTGRES_PASSWORD && %s --username=$carebot_POSTGRES_USER --host=$carebot_POSTGRES_HOST --port=$carebot_POSTGRES_PORT'

@task(default=True)
def update():
    """
    Stub function for updating app-specific data.
    """
    #update_featured_social()

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

    public_app.db.create_all()

@task
def bootstrap_db():
    for file in glob('data/queries/*.yaml'):
        with open(file, 'r') as f:
            data = yaml.load(f)

            query = public_app.Query()
            query.name = data['name']
            query.clan_yaml = yaml.dump(data, indent=4)

            public_app.db.session.add(query)
            public_app.db.session.commit()


@task
def run_reports():
    projects = public_app.Project.query.all()

    index_filename = 'clan_index.html'
    payload = {
        'projects': projects
    }

    with open('templates/%s' % index_filename) as f:
        template = Template(f.read())

    with open('/tmp/clan-index.html', 'w') as w:
        rendered = template.render(**payload)

        w.write(rendered)

    s3 = boto.connect_s3()

    # fake deployment target
    if not app_config.DEPLOYMENT_TARGET:
        app_config.configure_targets('staging')

    flat.deploy_file(
        s3,
        '/tmp/clan-index.html',
        '%s/reports/index.html' % (app_config.PROJECT_SLUG),
        app_config.DEFAULT_MAX_AGE
    )

    for project in projects:
        with open('/tmp/clan.yaml', 'w') as f:
            y = project.build_clan_yaml()
            f.write(y)

        local('clan report /tmp/clan.yaml /tmp/clan.html')

        flat.deploy_file(
            s3,
            '/tmp/clan.html',
            '%s/reports/%s/index.html' % (app_config.PROJECT_SLUG, project.slug),
            app_config.DEFAULT_MAX_AGE
        )

@task
def update_featured_social():
    """
    Update featured tweets
    """
    COPY = copytext.Copy(app_config.COPY_PATH)
    secrets = app_config.get_secrets()

    # Twitter
    print 'Fetching tweets...'

    twitter_api = Twitter(
        auth=OAuth(
            secrets['TWITTER_API_OAUTH_TOKEN'],
            secrets['TWITTER_API_OAUTH_SECRET'],
            secrets['TWITTER_API_CONSUMER_KEY'],
            secrets['TWITTER_API_CONSUMER_SECRET']
        )
    )

    tweets = []

    for i in range(1, 4):
        tweet_url = COPY['share']['featured_tweet%i' % i]

        if isinstance(tweet_url, copytext.Error) or unicode(tweet_url).strip() == '':
            continue

        tweet_id = unicode(tweet_url).split('/')[-1]

        tweet = twitter_api.statuses.show(id=tweet_id)

        creation_date = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
        creation_date = '%s %i' % (creation_date.strftime('%b'), creation_date.day)

        tweet_url = 'http://twitter.com/%s/status/%s' % (tweet['user']['screen_name'], tweet['id'])

        photo = None
        html = tweet['text']
        subs = {}

        for media in tweet['entities'].get('media', []):
            original = tweet['text'][media['indices'][0]:media['indices'][1]]
            replacement = '<a href="%s" target="_blank" onclick="_gaq.push([\'_trackEvent\', \'%s\', \'featured-tweet-action\', \'link\', 0, \'%s\']);">%s</a>' % (media['url'], app_config.PROJECT_SLUG, tweet_url, media['display_url'])

            subs[original] = replacement

            if media['type'] == 'photo' and not photo:
                photo = {
                    'url': media['media_url']
                }

        for url in tweet['entities'].get('urls', []):
            original = tweet['text'][url['indices'][0]:url['indices'][1]]
            replacement = '<a href="%s" target="_blank" onclick="_gaq.push([\'_trackEvent\', \'%s\', \'featured-tweet-action\', \'link\', 0, \'%s\']);">%s</a>' % (url['url'], app_config.PROJECT_SLUG, tweet_url, url['display_url'])

            subs[original] = replacement

        for hashtag in tweet['entities'].get('hashtags', []):
            original = tweet['text'][hashtag['indices'][0]:hashtag['indices'][1]]
            replacement = '<a href="https://twitter.com/hashtag/%s" target="_blank" onclick="_gaq.push([\'_trackEvent\', \'%s\', \'featured-tweet-action\', \'hashtag\', 0, \'%s\']);">%s</a>' % (hashtag['text'], app_config.PROJECT_SLUG, tweet_url, '#%s' % hashtag['text'])

            subs[original] = replacement

        for original, replacement in subs.items():
            html =  html.replace(original, replacement)

        # https://dev.twitter.com/docs/api/1.1/get/statuses/show/%3Aid
        tweets.append({
            'id': tweet['id'],
            'url': tweet_url,
            'html': html,
            'favorite_count': tweet['favorite_count'],
            'retweet_count': tweet['retweet_count'],
            'user': {
                'id': tweet['user']['id'],
                'name': tweet['user']['name'],
                'screen_name': tweet['user']['screen_name'],
                'profile_image_url': tweet['user']['profile_image_url'],
                'url': tweet['user']['url'],
            },
            'creation_date': creation_date,
            'photo': photo
        })

    # Facebook
    print 'Fetching Facebook posts...'

    fb_api = GraphAPI(secrets['FACEBOOK_API_APP_TOKEN'])

    facebook_posts = []

    for i in range(1, 4):
        fb_url = COPY['share']['featured_facebook%i' % i]

        if isinstance(fb_url, copytext.Error) or unicode(fb_url).strip() == '':
            continue

        fb_id = unicode(fb_url).split('/')[-1]

        post = fb_api.get_object(fb_id)
        user  = fb_api.get_object(post['from']['id'])
        user_picture = fb_api.get_object('%s/picture' % post['from']['id'])
        likes = fb_api.get_object('%s/likes' % fb_id, summary='true')
        comments = fb_api.get_object('%s/comments' % fb_id, summary='true')
        #shares = fb_api.get_object('%s/sharedposts' % fb_id)

        creation_date = datetime.strptime(post['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
        creation_date = '%s %i' % (creation_date.strftime('%b'), creation_date.day)

        # https://developers.facebook.com/docs/graph-api/reference/v2.0/post
        facebook_posts.append({
            'id': post['id'],
            'message': post['message'],
            'link': {
                'url': post['link'],
                'name': post['name'],
                'caption': (post['caption'] if 'caption' in post else None),
                'description': post['description'],
                'picture': post['picture']
            },
            'from': {
                'name': user['name'],
                'link': user['link'],
                'picture': user_picture['url']
            },
            'likes': likes['summary']['total_count'],
            'comments': comments['summary']['total_count'],
            #'shares': shares['summary']['total_count'],
            'creation_date': creation_date
        })

    # Render to JSON
    output = {
        'tweets': tweets,
        'facebook_posts': facebook_posts
    }

    with open('data/featured.json', 'w') as f:
        json.dump(output, f)
