#!/usr/bin/env python

from django.contrib import admin
from grappelli.forms import GrappelliSortableHiddenMixin

import app_config
from reports.models import Query, Project, ProjectQuery, Report

class QueryAdmin(admin.ModelAdmin):
    """
    Admin for the Query model.
    """
    fieldsets = (
        (None, {
            'fields': ('name', 'slug')
        }),
        (None, {
            'fields': ('clan_yaml',),
            'classes': ('monospace',)
        })
    )

    prepopulated_fields = { 'slug': ('name',) }

class ProjectQueryInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    """
    Admin for the ProjectQuery M2M inline.
    """
    model = ProjectQuery
    extra = 3 
    sortable_field_name = 'order'
    
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
    """
    Admin for the Project model.
    """
    fields = ('title', 'slug', 'property_id', 'domain', 'prefix', 'start_date')
    prepopulated_fields = { 'slug': ('title',) }

    list_display = ('title', 'property_id', 'domain', 'prefix', 'start_date', 'view_reports')
    list_display_links = ('title',)
    list_filter = ('property_id', 'domain')
    search_fields = ('title',)
    actions = (run_reports,)

    def change_view(self, *args, **kwargs):
        """
        Change view, with inlines.
        """
        self.inlines = (ProjectQueryInline,)

        return super(ProjectAdmin, self).change_view(*args, **kwargs)

    def add_view(self, *args, **kwargs):
        """
        Add view, without inlines.
        """
        self.inlines = ()

        return super(ProjectAdmin, self).add_view(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Save the model, adding references to default queries if needed.
        """
        add_default_queries = not bool(obj.pk)

        obj.save()

        if add_default_queries:
            for i, query_slug in enumerate(app_config.DEFAULT_QUERIES):
                ProjectQuery.objects.create(
                    project=obj,
                    query=Query.objects.get(slug=query_slug),
                    order=i
                )

    def view_reports(self, model):
        url = '%s/reports/%s/' % (app_config.S3_BASE_URL, model.slug)

        return '<a href="%s">View</a>' % url

    view_reports.allow_tags = True
    view_reports.short_description = 'Reports'

class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('results_json', 'last_run')
    list_display = ('project', 'ndays', 'last_run')
    list_display_links = ('ndays',)

admin.site.register(Query, QueryAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Report, ReportAdmin)

