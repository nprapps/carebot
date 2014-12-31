#!/usr/bin/env python

from collections import OrderedDict
from copy import copy
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
    slug = models.SlugField(max_length=128, primary_key=True)
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

class Tag(models.Model):
    """
    A tag describing a project.
    """
    slug = models.CharField(max_length=32, primary_key=True)

    class Meta:
        ordering = ('slug',)

    def __unicode__(self):
        return self.slug

class Project(models.Model):
    """
    A project (app/site).
    """
    slug = models.SlugField(max_length=128, primary_key=True)
    title = models.CharField(max_length=128)
    property_id = models.CharField(max_length=10, default='53470309')
    domain = models.CharField(max_length=128, default='apps.npr.org')
    prefix = models.CharField(max_length=128)
    start_date = models.DateField()
    queries = models.ManyToManyField(Query, through='ProjectQuery')
    tags = models.ManyToManyField(Tag)

    class Meta:
        ordering = ('-start_date',)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reports.views.project', args=[self.slug])

    def tag_list(self):
        return ','.join([tag.slug for tag in self.tags.all()])
    
    @property
    def all_time_report(self):
        return self.reports.get(ndays__isnull=True)

    def run_reports(self, overwrite=False):
        """
        Runs all reports, optionally overwriting existing results.
        """
        print 'Running reports for %s' % self.title
        
        updated_reports = []

        for report in self.reports.all():
            if overwrite or not report.last_run:
                updated = report.run()

                if updated and report.ndays:
                    updated_reports.append(report)
            else:
                print 'Skipping %s report for %s (already run).' % (report.timespan, self.title)

        return updated_reports

    def get_clan_config(self):
        return {
            'title': self.title,
            'property-id': self.property_id,
            'domain': self.domain,
            'prefix': self.prefix,
            'start-date': datetime.strftime(self.start_date, '%Y-%m-%d')
        }

@receiver(models.signals.post_save, sender=Project)
def on_project_post_save(sender, instance, created, *args, **kwargs):
    """
    Create default reports for a new project.
    """
    if created:
        default_queries = copy(app_config.DEFAULT_QUERIES)

        if instance.start_date > date(2014, 6, 1):
            default_queries.extend(app_config.DEFAULT_EVENT_QUERIES)

        for i, query_slug in enumerate(default_queries):
            ProjectQuery.objects.create(
                project=instance,
                query=Query.objects.get(slug=query_slug),
                order=i
            )

        Report.objects.create(
            project=instance,
            ndays=None
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
    ndays = models.PositiveIntegerField(null=True)
    results_json = models.TextField()
    last_run = models.DateTimeField(null=True)

    pageviews = models.PositiveIntegerField(null=True)
    unique_pageviews = models.PositiveIntegerField(null=True)
    users = models.PositiveIntegerField(null=True)
    sessions = models.PositiveIntegerField(null=True)

    class Meta:
        ordering = ('project__start_date', 'ndays',)

    def __unicode__(self):
        return '%s (%s)' % (self.project.title, self.timespan)

    def get_absolute_url(self):
        return reverse(
            'reports.views.report',
            args=[
                self.project.slug,
                self.ndays or 'all-time'
            ]
        )

    @property
    def timespan(self):
        if self.ndays:
            return '%i-day%s' % (self.ndays, 's' if self.ndays > 1 else '')

        return 'all-time'

    def is_timely(self):
        """
        Checks if it has been long enough to have data for this report.
        """
        if not self.ndays:
            return True

        return date.today() >= self.project.start_date + timedelta(days=self.ndays)

    def build_clan_yaml(self):
        """
        Build YAML configuration for this report.
        """
        data = self.project.get_clan_config() 

        if self.ndays:
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
            print 'Skipping %s report for %s (not timely).' % (self.timespan, self.project.title)
            return False
            
        print 'Running %s report for %s' % (self.timespan, self.project.title)

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
            project_title = self.project.title
            query = project_query.query
            query_name = query.name
            metrics = result['config']['metrics']
            data_types = result['data_types']

            qr = QueryResult(
                report=self,
                query=query,
                order=i,
                sampled=result['sampled'],
                project_title=project_title,
                report_ndays=self.ndays,
                query_name=query_name
            )

            if result['sampled']:
                qr.sample_size = result['sampleSize']
                qr.sample_space = result['sampleSpace']
                qr.sample_percent = float(result['sampleSize']) / result['sampleSpace'] * 100

            qr.save()

            j = 0

            # Metrics
            for metric_name in metrics:
                self._make_metric(
                    qr,
                    metric_name,
                    j,
                    data_types[metric_name],
                    result['data'][metric_name]
                )

                j += 1
                
            i += 1

        qr = self.query_results.get(query__slug='totals')
        
        for metric in qr.metrics.all():
            if metric.name == 'ga:pageviews':
                self.pageviews = metric.total_dimension.value
            elif metric.name == 'ga:uniquePageviews':
                self.unique_pageviews = metric.total_dimension.value
            elif metric.name == 'ga:users':
                self.users = metric.total_dimension.value
            elif metric.name == 'ga:sessions':
                self.sessions = metric.total_dimension.value

        self.save()

        return True

    def _make_metric(self, query_result, metric_name, order, data_type, dimensions):
        """
        Create a Metric and related Dimensions.
        """
        total_value = dimensions['total']

        metric = MetricResult(
            query_result=query_result,
            order=order,
            name=metric_name,
            data_type=data_type,
            project_title=query_result.project_title,
            report_ndays=query_result.report_ndays,
            query_name=query_result.query_name
        )

        metric.save()

        i = 0

        # Dimensions
        for dimension_name, value in dimensions.items():
            self._make_dimension(
                metric,
                dimension_name,
                i,
                data_type,
                value,
                total_value
            )

            i += 1

    def _make_dimension(self, metric, dimension_name, order, data_type, value, total_value):
        """
        Create a new Dimension.
        """
        dimension = DimensionResult(
            order=order,
            name=dimension_name,
            _value=value,
            project_title=metric.project_title,
            report_ndays=metric.report_ndays,
            query_name=metric.query_name,
            metric_name=metric.name,
            metric_data_type=metric.data_type
        )

        if dimension_name != 'total':
            if data_type in 'INTEGER' and total_value != 0: 
                dimension.percent_of_total = float(value) / int(total_value) * 100

        dimension.metric = metric
        dimension.save()

        return dimension

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

    # Denormalized fields
    project_title = models.CharField(max_length=128)
    report_ndays = models.PositiveIntegerField(null=True)
    query_name = models.CharField(max_length=128)

    class Meta:
        ordering = ('report', 'order')

class MetricResult(models.Model):
    """
    The results for a specific metric.
    """
    query_result = models.ForeignKey(QueryResult, related_name='metrics')
    order = models.PositiveIntegerField()

    name = models.CharField(max_length=128)
    data_type = models.CharField(max_length=30)

    # Denormalized fields
    project_title = models.CharField(max_length=128)
    report_ndays = models.PositiveIntegerField(null=True)
    query_name = models.CharField(max_length=128)

    class Meta:
        ordering = ('query_result', 'order')

    def __unicode__(self):
        return self.name

    @property
    def display_name(self):
        return FIELD_DEFINITIONS[self.name]['uiName']

    @property
    def total_dimension(self):
        return self.dimensions.get(name='total')

class DimensionResult(models.Model):
    """
    Results for one dimension of a metric.
    """
    metric = models.ForeignKey(MetricResult, related_name='dimensions', null=True)
    order = models.PositiveIntegerField()

    name = models.CharField(max_length=128)
    _value = models.CharField(max_length=128)
    percent_of_total = models.FloatField(null=True)

    # Denormalized fields
    project_title = models.CharField(max_length=128)
    report_ndays = models.PositiveIntegerField(null=True)
    query_name = models.CharField(max_length=128)
    metric_name = models.CharField(max_length=128)
    metric_data_type = models.CharField(max_length=30)

    class Meta:
        ordering = ('metric', 'order')

    @property
    def value(self):
        if self.metric_data_type == 'INTEGER':
            return int(self._value)
        elif self.metric_data_type == 'STRING':
            return self._value
        elif self.metric_data_type in ['FLOAT', 'PERCENT', 'TIME', 'CURRENCY']:
            return float(self._value)

        return None

    @property
    def value_formatted(self):
        if self.metric_data_type == 'INTEGER':
            return utils.format_comma(int(self._value))
        elif self.metric_data_type == 'STRING':
            return self._value
        elif self.metric_data_type in ['FLOAT', 'PERCENT', 'CURRENCY']:
            return '%.1f' % float(self._value)
        elif self.metric_data_type == 'TIME':
            return clan_utils.format_duration(float(self._value))

        return None

    @property
    def per_session(self):
        if self.metric_data_type != 'INTEGER':
            return None

        return float(self.value) / self.metric.query_result.report.sessions

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
        ordering = ('-project__start_date',)
        verbose_name = 'social count'
        verbose_name_plural = 'social counts'

    def __unicode__(self):
        return 'Social counts for %s' % self.project.title

    def total(self):
        return sum([
            self.facebook_likes,
            self.facebook_shares,
            self.facebook_comments,
            self.twitter,
            self.google,
            self.pinterest,
            self.linkedin,
            self.stumbleupon
        ])

    def refresh(self):
        secrets = app_config.get_secrets()

        url = 'http://%s%s' % (self.project.domain, self.project.prefix)
        response = requests.get('https://free.sharedcount.com/url?apikey=%s&url=%s' % (secrets['SHAREDCOUNT_API_KEY'], url))

        if response.status_code != 200:
            print 'Failed to refresh social data from SharedCount: %i.' % response.status_code
            return

        print 'Updating social counts from SharedCount'

        data = response.json()

        self.facebook_likes = data['Facebook']['like_count'] or 0
        self.facebook_shares = data['Facebook']['share_count'] or 0
        self.facebook_comments = data['Facebook']['comment_count'] or 0
        self.twitter = data['Twitter'] or 0
        self.google = data['GooglePlusOne'] or 0
        self.pinterest = data['Pinterest'] or 0
        self.linkedin = data['LinkedIn'] or 0
        self.stumbleupon = data['StumbleUpon'] or 0

        self.last_update = timezone.now()

        self.save()

