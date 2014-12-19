#!/usr/bin/env python

from django.contrib import admin
from grappelli.forms import GrappelliSortableHiddenMixin

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

        print args
        print kwargs
        #print kwargs['instance']
        #print self.initial

class ProjectAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'property_id', 'domain', 'prefix', 'start_date')
    prepopulated_fields = { 'slug': ('title',) }
    inlines = (ProjectQueryInline,)

    list_display = ('title', 'property_id', 'domain', 'prefix', 'start_date')
    list_display_links = ('title',)
    list_filter = ('property_id', 'domain')
    search_fields = ('title')

admin.site.register(Query, QueryAdmin)
admin.site.register(Project, ProjectAdmin)

