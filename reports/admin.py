#!/usr/bin/env python

from django.contrib import admin

from reports.models import Query, Project

admin.site.register(Query)
admin.site.register(Project)

