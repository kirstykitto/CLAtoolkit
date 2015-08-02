
from django.conf.urls import patterns, url

from dataintegration import views

urlpatterns = patterns(
    url(r'^home/$', views.home, name='home'),
    url(r'^login/(?P<group_id>\d+)$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^get_social/$', views.get_social_media_id, name='get_social'),
    url(r'^refreshtwitter/$', views.refreshtwitter, name='refreshtwitter')
)
