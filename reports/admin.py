#!/usr/bin/env python

from django.contrib import admin
from grappelli.forms import GrappelliSortableHiddenMixin

from reports import models

class QueryAdmin(admin.ModelAdmin):
    """
    Admin for the Query model.
    """
    list_display = ('name', 'description') 

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        (None, {
            'fields': ('clan_yaml',),
            'classes': ('monospace',)
        })
    )

    prepopulated_fields = { 'slug': ('name',) }

class TagInline(admin.TabularInline):
    model = models.Project.tags.through
    extra = 2

class ProjectQueryInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    """
    Admin for the ProjectQuery M2M inline.
    """
    model = models.ProjectQuery
    extra = 3 
    sortable_field_name = 'order'
    
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin for the Project model.
    """
    fields = ('title', 'slug', 'property_id', 'domain', 'prefix', 'start_date')
    prepopulated_fields = { 'slug': ('title',) }

    list_display = ('title', 'tag_list', 'property_id', 'domain', 'prefix', 'start_date', 'view_reports')
    list_display_links = ('title',)
    list_filter = ('property_id', 'domain')
    search_fields = ('title',)

    def change_view(self, *args, **kwargs):
        """
        Change view, with inlines.
        """
        self.inlines = (TagInline, ProjectQueryInline,)

        return super(ProjectAdmin, self).change_view(*args, **kwargs)

    def add_view(self, *args, **kwargs):
        """
        Add view, without inlines.
        """
        self.inlines = (TagInline,)

        return super(ProjectAdmin, self).add_view(*args, **kwargs)

    def tag_list(self, model):
        return model.tag_list() 

    tag_list.short_description = 'Tags'

    def view_reports(self, model):
        return '<a href="%s">View</a>' % model.get_absolute_url()

    view_reports.allow_tags = True
    view_reports.short_description = 'Reports'

class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('results_json', 'last_run')
    list_display = ('project', 'ndays', 'last_run', 'view_report')
    list_display_links = ('ndays',)

    def view_report(self, model):
        if not model.last_run:
            return None
        else:
            return '<a href="%s">View</a>' % model.get_absolute_url() 

    view_report.allow_tags = True
    view_report.short_description = 'View'

class QueryResultAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'report_ndays', 'query_name')
    list_display_links = ('query_name',)

class MetricResultAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'report_ndays', 'query_name', 'name')
    list_display_links = ('name',)

class DimensionResultAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'report_ndays', 'query_name', 'metric_name', 'name', 'value', 'percent_of_total')
    list_display_links = ('name',)

class SocialAdmin(admin.ModelAdmin):
    list_display = ('project', 'facebook_likes', 'facebook_shares', 'facebook_comments', 'twitter', 'google', 'pinterest', 'linkedin', 'stumbleupon')
    list_display_links = ('project',)

admin.site.register(models.Query, QueryAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Report, ReportAdmin)
admin.site.register(models.Social, SocialAdmin)
#admin.site.register(models.QueryResult, QueryResultAdmin)
#admin.site.register(models.MetricResult, MetricResultAdmin)
#admin.site.register(models.DimensionResult, DimensionResultAdmin)
