#!/usr/bin/env python

from collections import OrderedDict
from datetime import date, datetime, timedelta
from itertools import izip
import json
import subprocess

from clan import utils as clan_utils
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver 
from django.utils import timezone
import requests
import yaml

import app_config
import utils

FIELD_DEFINITIONS = clan_utils.load_field_definitions()

class Query(models.Model):
    """
    A clan query.
    """
    slug = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256, default='')
    clan_yaml = models.TextField()

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'queries'

    def __unicode__(self):
        return self.name 

    @property
    def config(self):
        data = yaml.load(self.clan_yaml)

        data['name'] = self.name
        data['description'] = self.description

        return data 

class Project(models.Model):
    """
    A project (app/site).
    """
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
    """
    Create default reports for a new project.
    """
    if created:
        for i, query_slug in enumerate(app_config.DEFAULT_QUERIES):
            ProjectQuery.objects.create(
                project=instance,
                query=Query.objects.get(slug=query_slug),
                order=i
            )

        for ndays in app_config.DEFAULT_REPORT_NDAYS:
            Report.objects.create(
                project=instance,
                ndays=ndays
            )

        Social.objects.create(project=instance)

class ProjectQuery(models.Model):
    """
    M2M relationship between Projects and Queries.
    """
    project = models.ForeignKey(Project, related_name='project_queries')
    query = models.ForeignKey(Query, related_name='project_queries')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order',)

class Report(models.Model):
    """
    A report for a given project over some number of days.
    """
    project = models.ForeignKey(Project, related_name='reports')
    ndays = models.PositiveIntegerField()
    results_json = models.TextField()
    last_run = models.DateTimeField(null=True)

    class Meta:
        ordering = ('project__start_date', 'ndays',)

    def __unicode__(self):
        return '%s (%i-day%s)' % (self.project.title, self.ndays, 's' if self.ndays > 1 else '')

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
            data['queries'].append(project_query.query.config)

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

        # Delete existing results
        self.query_results.all().delete()

        data = json.loads(self.results_json, object_pairs_hook=OrderedDict)
        i = 0

        # Query results
        for project_query, result in izip(self.project.project_queries.all(), data['queries']):
            query = project_query.query
            metrics = result['config']['metrics']
            data_types = result['data_types']

            qr = QueryResult(
                report=self,
                query=query,
                order=i,
                sampled=result['sampled']
            )

            if result['sampled']:
                qr.sample_size = result['sampleSize']
                qr.sample_space = result['sampleSpace']
                qr.sample_percent = result['sampleSize'] / result['sampleSpace'] * 100

            qr.save()

            j = 0

            # Metrics
            for metric in metrics:
                dimensions = result['data'][metric]
                data_type = data_types[metric]
                total = result['data'][metric]['total']

                m = Metric(
                    query_result=qr,
                    order=j,
                    name=metric,
                    data_type=data_type
                )

                m.save()

                k = 0

                # Dimensions
                for dimension, value in dimensions.items():
                    d = Dimension(
                        metric=m,
                        order=k,
                        name=dimension,
                        _value=value
                    )

                    if data_type in 'INTEGER': 
                        d.percent_of_total = float(value) / total * 100

                    d.save()

                    k += 1
                
                j += 1
                
            i += 1

        self.save()

        return True

class QueryResult(models.Model):
    """
    The results of a query for a certain report.
    """
    report = models.ForeignKey(Report, related_name='query_results')
    query = models.ForeignKey(Query, related_name='query_results')
    order = models.PositiveIntegerField()

    sampled = models.BooleanField(default=False)
    sample_size = models.PositiveIntegerField(default=0)
    sample_space = models.PositiveIntegerField(default=0)
    sample_percent = models.FloatField(default=100)

    class Meta:
        ordering = ('report', 'order')

class Metric(models.Model):
    """
    The results for a specific metric.
    """
    query_result = models.ForeignKey(QueryResult, related_name='metrics')
    order = models.PositiveIntegerField()

    name = models.CharField(max_length=128)
    data_type = models.CharField(max_length=30)

    class Meta:
        ordering = ('query_result', 'order')

    def __unicode__(self):
        return self.name

    @property
    def display_name(self):
        return FIELD_DEFINITIONS[self.name]['uiName']

class Dimension(models.Model):
    """
    Results for one dimension of a metric.
    """
    metric = models.ForeignKey(Metric, related_name='dimensions')
    order = models.PositiveIntegerField()

    name = models.CharField(max_length=128)
    _value = models.CharField(max_length=128)
    percent_of_total = models.FloatField(null=True)

    class Meta:
        ordering = ('metric', 'order')

    @property
    def value(self):
        if self.metric.data_type == 'INTEGER':
            return int(self._value)
        elif self.metric.data_type == 'STRING':
            return self._value
        elif self.metric.data_type in ['FLOAT', 'PERCENT', 'TIME', 'CURRENCY']:
            return float(self._value)

        return None

    @property
    def value_formatted(self):
        if self.metric.data_type == 'INTEGER':
            return utils.format_comma(int(self._value))
        elif self.metric.data_type == 'STRING':
            return self._value
        elif self.metric.data_type in ['FLOAT', 'PERCENT', 'CURRENCY']:
            return '%.1f' % float(self._value)
        elif self.metric.data_type == 'TIME':
            return clan_utils.format_duration(float(self._value))

        return None

class Social(models.Model):
    """
    Social count data for a project. NOT timeboxed.
    """
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
        verbose_name = 'social count'
        verbose_name_plural = 'social counts'

    def __unicode__(self):
        return 'Social counts for %s' % self.project.title

    def refresh(self):
        secrets = app_config.get_secrets()

        url = 'http://%s%s' % (self.project.domain, self.project.prefix)
        response = requests.get('https://free.sharedcount.com/url?apikey=%s&url=%s' % (secrets['SHAREDCOUNT_API_KEY'], url))

        if response.status_code != 200:
            print 'Failed to refresh social data from SharedCount.'
            return

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
