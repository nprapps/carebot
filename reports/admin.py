#!/usr/bin/env python

from django.contrib import admin
from grappelli.forms import GrappelliSortableHiddenMixin

import app_config
from reports.models import Query, Project, ProjectQuery

class QueryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'clan_yaml')
    prepopulated_fields = { 'slug': ('name',) }

class ProjectQueryInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = ProjectQuery
    extra = 3 
    sortable_field_name = 'order'

    def __init__(self, *args, **kwargs):
        super(ProjectQueryInline, self).__init__(*args, **kwargs)

def run_reports(model_admin, request, queryset):
    """
    Run reports for selected projects.
    """
    import boto

    s3 = boto.connect_s3()

    for model in queryset:
        model.run_report(s3=s3)

run_reports.short_description = 'Run reports'

class ProjectAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'property_id', 'domain', 'prefix', 'start_date')
    prepopulated_fields = { 'slug': ('title',) }
    inlines = (ProjectQueryInline,)

    list_display = ('title', 'property_id', 'domain', 'prefix', 'start_date', 'view_reports')
    list_display_links = ('title',)
    list_filter = ('property_id', 'domain')
    search_fields = ('title',)
    actions = (run_reports,)

    def view_reports(self, model):
        url = '%s/reports/%s/' % (app_config.S3_BASE_URL, model.slug)

        return '<a href="%s">View</a>' % url

    view_reports.allow_tags = True
    view_reports.short_description = 'Reports'

admin.site.register(Query, QueryAdmin)
admin.site.register(Project, ProjectAdmin)

