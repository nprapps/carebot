#!/usr/bin/env python

from datetime import datetime
import yaml

from django.db import models

class Query(models.Model):
    slug = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    clan_yaml = models.TextField()

    def __unicode__(self):
       return self.slug

class Project(models.Model):
    slug = models.SlugField(max_length=128, unique=True)
    title = models.CharField(max_length=128)
    property_id = models.CharField(max_length=10, default='53470309')
    domain = models.CharField(max_length=128, default='apps.npr.org')
    prefix = models.CharField(max_length=128)
    start_date = models.DateField()
    queries = models.ManyToManyField(Query)

    def __unicode__(self):
        return self.slug

    def build_clan_yaml(self):
        data = { }

        if self.title:
            data['title'] = self.title
        if self.property_id:
            data['property-id'] = self.property_id
        if self.domain:
            data['domain'] = self.domain
        if self.prefix:
            data['prefix'] = self.prefix
        if self.start_date:
            data['start-date'] = datetime.strftime(self.start_date, '%Y-%m-%d')
        if self.queries:
            data['queries'] = []

        for query in self.queries.all():
            y = yaml.load(query.clan_yaml)

            data['queries'].append(y)

        # snowman
        return yaml.safe_dump(data, encoding='utf-8', allow_unicode=True)

