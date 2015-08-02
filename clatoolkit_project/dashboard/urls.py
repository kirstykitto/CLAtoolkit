
from django.conf.urls import patterns, url, include
from django.contrib import admin

import views

urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^myunits/$', views.myunits, name='myunits'),
    url(r'^ca_dashboard/$', views.cadashboard, name='cadashboard'),
    url(r'^sna_dashboard/$', views.snadashboard, name='snadashboard'),
    url(r'^student_dashboard/$', views.studentdashboard, name='studentdashboard'),
    url(r'^pyldavis/$', views.pyldavis, name='pyldavis')
)
