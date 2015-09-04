from django.conf.urls import patterns, url, include
from django.contrib import admin

import views

urlpatterns = patterns('',
    url(r'^register/$', views.register, name='register'),
    url(r'^eventregistration/$', views.eventregistration, name='eventregistration'),
)
