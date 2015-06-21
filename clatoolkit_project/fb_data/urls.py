# example/simple/urls.py

from django.conf.urls import patterns, url

from fb_data import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^login/(?P<group_id>\d+)$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^get_social/$', views.get_social_media_id, name='get_social')
)
