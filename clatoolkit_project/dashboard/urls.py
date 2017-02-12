
from django.conf.urls import patterns, url, include
from django.contrib import admin

import views

urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^myunits/$', views.myunits, name='myunits'),
    url(r'^ca_dashboard/$', views.cadashboard, name='cadashboard'),
    url(r'^sna_dashboard/$', views.snadashboard, name='snadashboard'),
    url(r'^student_dashboard/$', views.studentdashboard, name='studentdashboard'),
    url(r'^mydashboard/$', views.mydashboard, name='mydashboard'),
    url(r'^pyldavis/$', views.pyldavis, name='pyldavis'),
    url(r'^myclassifications/$', views.myclassifications, name='myclassifications'),
    url(r'^ccadashboard/$', views.ccadashboard, name='ccadashboard'),
    url(r'^getBoards/$', views.get_trello_boards, name='gettrelloboards'),
    url(r'^addboardtocourse/$', views.add_board_to_course, name='addboardtocourse'),
    url(r'^removeBoard/$', views.trello_remove_board, name='removetrelloboard'),
    
    #REST
    url(r'^getAttachedBoard/$', views.trello_myunits_restview, name='gettrellodashboardlink'),
    url(r'^api/get_platform_timeseries_data/$', views.get_platform_timeseries_data, name='get_platform_timeseries_data'),
    url(r'^api/get_platform_activities/$', views.get_platform_activities, name='get_platform_activities'),
    url(r'^api/getAllRepos/$', views.get_all_repos, name='get_all_repos'),
    url(r'^api/addRepoToCourse/$', views.add_repo_to_course, name='add_repo_to_course'),
    url(r'^api/getGitHubAttachedRepo/$', views.get_github_attached_repo, name='get_github_attached_repo'),
    url(r'^api/removeAttachedRepo$', views.remove_attached_repo, name='remove_attached_repo'),
    url(r'^api/get_user_acitivities/$', views.get_user_acitivities, name='get_user_acitivities'),
    url(r'^api/get_github_contribution/$', views.get_github_contribution, name='get_github_contribution'),
    url(r'^api/get_learning_records/$', views.get_learning_records, name='get_learning_records'),
)
