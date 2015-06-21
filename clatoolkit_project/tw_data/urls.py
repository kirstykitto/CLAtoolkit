# example/simple/urls.py

from django.conf.urls import patterns, url

from tw_data import views

urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^twitter/(?P<account>[^/]+)/(?P<sent_hashtag>[^/]+)$', views.twitter, name='twitter'),
                       )
