from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from carebot import settings

urlpatterns = patterns('',
    url(r'^carebot/grappelli/', include('grappelli.urls')),
    url(r'^carebot/admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
