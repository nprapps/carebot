from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from carebot import settings
from reports import views

urlpatterns = patterns('',
    url(r'^carebot/$', views.index),
    url(r'^carebot/compare-query/$', views.compare_query),
    url(r'^carebot/project/(?P<slug>[\w-]+)/$', views.project),
    url(r'^carebot/report/(?P<slug>[\w-]+)/(?P<ndays>\d+)/$', views.report),
    url(r'^carebot/grappelli/', include('grappelli.urls')),
    url(r'^carebot/admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
