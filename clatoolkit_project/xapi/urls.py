from django.conf.urls import patterns, url

import views

urlpatterns = patterns('xapi.views',
    url(r'^$', views.lrs_test_view, name='lrs_test_view'),
    url(r'^send_statment/$', views.lrs_test_send, name='lrs_test_send'),
    url(r'^get_statement/$', views.lrs_test_get_statements, name='lrs_test_get_statements'),
    url(r'^lrsauth_callback/$', views.lrs_oauth_callback, name='lrs_oauth_callback')
)