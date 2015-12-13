
from django.conf.urls import patterns, url, include
from views import LTILaunch
from dashboard import views
from django.contrib import admin

import views

urlpatterns = patterns('',
    url(r'^launch/$', LTILaunch.as_view(), name='launch_clatoolkit_lti')

)