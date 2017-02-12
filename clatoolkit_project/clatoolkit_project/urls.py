from django.conf.urls import patterns, include, url
from django.contrib import admin
from clatoolkit import views

from clatoolkit.urls import router

urlpatterns = patterns('',
    url(r'^$', views.userlogin, name='userlogin'),
    url(r'^clatoolkit/', include('clatoolkit.urls')),
    url(r'^api/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dataintegration/', include('dataintegration.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^xapi/', include('xapi.urls')),
    url(r'^logout/(?P<next_page>.*)/$', 'django.contrib.auth.views.logout', name='auth_logout_next'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
)
