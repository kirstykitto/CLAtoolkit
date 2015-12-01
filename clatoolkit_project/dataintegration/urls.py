
from django.conf.urls import patterns, url

from dataintegration import views

urlpatterns = patterns(
    url(r'^home/$', views.home, name='home'),
    url(r'^login/(?P<group_id>\d+)$', views.login, name='login'),
    url(r'^get_social/$', views.get_social_media_id, name='get_social'),
    url(r'^refreshtwitter/$', views.refreshtwitter, name='refreshtwitter'),
    url(r'^refreshforum/$', views.refreshforum, name='refreshforum'),
    url(r'^sendtolrs/$', views.sendtolrs, name='sendtolrs'),
    url(r'^updatelearningrecords/$', views.updatelearningrecords, name='updatelearningrecords'),
    url(r'^insertsocialrelationships/$', views.insertsocialrelationships, name='insertsocialrelationships'),
    url(r'^refreshyoutube/$', views.refreshyoutube, name='refreshyoutube'),
    url(r'^ytAuthCallback/$', views.ytAuthCallback, name='ytAuthCallback'),
    url(r'^get_youtubechannel/$', views.get_youtubechannel, name='get_youtubechannel'),
    url(r'^assigngroups/$', views.assigngroups, name='assigngroups')
)
