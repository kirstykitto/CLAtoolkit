from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', include('clatoolkit.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dataintegration/', include('dataintegration.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
)
