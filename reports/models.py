#!/usr/bin/env python

from datetime import date, datetime, timedelta
import subprocess

from django.db import models
from django.dispatch import receiver 
import yaml

import app_config
import flat

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

    def run_reports(self, overwrite=False):
        """
        Runs all reports, optionally overwriting existing results.
        """
        for report in self.reports.all():
            if overwrite or not report.last_run:
                report.run()

@receiver(models.signals.post_save, sender=Project)
def on_project_post_save(sender, instance, created, *args, **kwargs):
    if created:
        for ndays in app_config.DEFAULT_REPORT_NDAYS:
            Report.objects.create(
                project=instance,
                ndays=ndays
            )

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
    last_run = models.DateTimeField(null=True)

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

    def run(self, s3=None):
        """
        Run this report, stash it's results and render it out to S3.
        """
        if not self.is_timely():
            print 'Skipping %i-day report for %s (not timely).' % (self.ndays, self.project.title)
            return
            
        print 'Running %i-day report for %s' % (self.ndays, self.project.title)

        with open('/tmp/clan.yaml', 'w') as f:
            y = self.build_clan_yaml()
            f.write(y)

        subprocess.call(['clan', 'report', '/tmp/clan.yaml', '/tmp/clan.json'])

        with open('/tmp/clan.json') as f:
            self.results_json = f.read() 
            self.last_run = datetime.now()
            self.save()

        subprocess.call(['clan', 'report', '/tmp/clan.json', '/tmp/clan.html'])

        if not s3:
            import boto

            s3 = boto.connect_s3()

        flat.deploy_file(
            s3,
            '/tmp/clan.html',
            '%s/reports/%s/%i-days/index.html' % (app_config.PROJECT_SLUG, self.project.slug, self.ndays),
            app_config.DEFAULT_MAX_AGE
        )


