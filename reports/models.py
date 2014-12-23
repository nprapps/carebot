#!/usr/bin/env python

from datetime import date, datetime, timedelta
import subprocess

from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver 
from django.utils import timezone
import requests
import yaml

import app_config

class Query(models.Model):
    slug = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    clan_yaml = models.TextField()

    def __unicode__(self):
       return self.name 

class Project(models.Model):
    slug = models.SlugField(max_length=128, unique=True)
    title = models.CharField(max_length=128)
    property_id = models.CharField(max_length=10, default='53470309')
    domain = models.CharField(max_length=128, default='apps.npr.org')
    prefix = models.CharField(max_length=128)
    start_date = models.DateField()
    queries = models.ManyToManyField(Query, through='ProjectQuery')

    class Meta:
        ordering = ('start_date',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reports.views.project', args=[self.slug])

    def run_reports(self, overwrite=False):
        """
        Runs all reports, optionally overwriting existing results.
        """
        updated_reports = []

        for report in self.reports.all():
            if overwrite or not report.last_run:
                updated = report.run()

                if updated:
                    updated_reports.append(report)
            else:
                print 'Skipping %i-day report for %s (already run).' % (report.ndays, self.title)

        return updated_reports

@receiver(models.signals.post_save, sender=Project)
def on_project_post_save(sender, instance, created, *args, **kwargs):
    if created:
        for ndays in app_config.DEFAULT_REPORT_NDAYS:
            Report.objects.create(
                project=instance,
                ndays=ndays
            )

        Social.objects.create(project=instance)

class ProjectQuery(models.Model):
    project = models.ForeignKey(Project)
    query = models.ForeignKey(Query)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order',)

class Report(models.Model):
    project = models.ForeignKey(Project, related_name='reports')
    ndays = models.PositiveIntegerField()
    results_json = models.TextField()
    results_html = models.TextField()
    last_run = models.DateTimeField(null=True)

    class Meta:
        ordering = ('project__start_date', 'ndays',)

    def get_absolute_url(self):
        return reverse('reports.views.report', args=[self.project.slug, unicode(self.ndays)])

    def is_timely(self):
        """
        Checks if it has been long enough to have data for this report.
        """
        return date.today() >= self.project.start_date + timedelta(days=self.ndays)

    def build_clan_yaml(self):
        """
        Build YAML configuration for this report.
        """
        data = {}

        data['title'] = self.project.title
        data['property-id'] = self.project.property_id
        data['domain'] = self.project.domain
        data['prefix'] = self.project.prefix
        data['start-date'] = datetime.strftime(self.project.start_date, '%Y-%m-%d')
        data['ndays'] = self.ndays
        data['queries'] = []

        for project_query in ProjectQuery.objects.filter(project=self.project):
            y = yaml.load(project_query.query.clan_yaml)

            data['queries'].append(y)

        return yaml.safe_dump(data, encoding='utf-8', allow_unicode=True)

    def run(self):
        """
        Run this report, stash it's results and render it out to S3.
        """
        if not self.is_timely():
            print 'Skipping %i-day report for %s (not timely).' % (self.ndays, self.project.title)
            return False
            
        print 'Running %i-day report for %s' % (self.ndays, self.project.title)

        with open('/tmp/clan.yaml', 'w') as f:
            y = self.build_clan_yaml()
            f.write(y)

        subprocess.call(['clan', 'report', '/tmp/clan.yaml', '/tmp/clan.json'])

        with open('/tmp/clan.json') as f:
            self.results_json = f.read() 
            self.last_run = timezone.now()

        subprocess.call(['clan', 'report', '/tmp/clan.json', '/tmp/clan.html'])

        with open('/tmp/clan.html') as f:
            self.results_html = f.read()

        self.save()

        return True

class Social(models.Model):
    project = models.OneToOneField(Project, primary_key=True)

    facebook_likes = models.PositiveIntegerField(default=0)
    facebook_shares = models.PositiveIntegerField(default=0)
    facebook_comments = models.PositiveIntegerField(default=0)
    twitter = models.PositiveIntegerField(default=0)
    google = models.PositiveIntegerField(default=0)
    pinterest = models.PositiveIntegerField(default=0)
    linkedin = models.PositiveIntegerField(default=0)
    stumbleupon = models.PositiveIntegerField(default=0)

    last_update = models.DateTimeField(null=True)

    class Meta:
        ordering = ('project__start_date',)

    def __unicode__(self):
        return 'Social counts for %s' % self.project.title

    def refresh(self):
        secrets = app_config.get_secrets()

        url = 'http://%s%s' % (self.project.domain, self.project.prefix)
        response = requests.get('https://free.sharedcount.com/url?apikey=%s&url=%s' % (secrets['SHAREDCOUNT_API_KEY'], url))

        data = response.json()

        self.facebook_likes = data['Facebook']['like_count']
        self.facebook_shares = data['Facebook']['share_count']
        self.facebook_comments = data['Facebook']['comment_count']
        self.twitter = data['Twitter']
        self.google = data['GooglePlusOne']
        self.pinterest = data['Pinterest']
        self.linkedin = data['LinkedIn']
        self.stumbleupon = data['StumbleUpon']

        self.last_update = timezone.now()

        self.save()
