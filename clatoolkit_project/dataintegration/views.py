# example/simple/views.py
from __future__ import absolute_import

from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from authomatic import Authomatic
from authomatic.adapters import DjangoAdapter
from authomatic.providers import oauth2
from dashboard.utils import *
from django.template import RequestContext
from dataintegration.tasks import *
from .forms import FacebookGatherForm
import json
from pprint import pprint
from clatoolkit.models import UnitOffering, DashboardReflection, LearningRecord, SocialRelationship, CachedContent, GroupMap, OauthFlowTemp
from django.db import connection
import dateutil.parser
from dashboard.utils import *
from dataintegration.groupbuilder import *
from dataintegration.core.processingpipeline import *
from dataintegration.core.recipepermissions import *

from django.conf import settings

from rest_framework.decorators import api_view

from dataintegration.googleLib import *
from oauth2client.client import OAuth2WebServerFlow
from django.contrib.sites.shortcuts import get_current_site

##############################################
# Data Extraction for YouTube
##############################################
def refreshgoogleauthflow(request):
    course_code = request.GET.get('course_code')
    channelIds = request.GET.get('channelIds')
    platform = courseId = request.GET.get('platform')

    user = request.user
    youtube_plugin = settings.DATAINTEGRATION_PLUGINS['YouTube']

    redirecturl= 'http://' + get_current_site(request).domain + '/dataintegration/ytAuthCallback'

    # store request data in temp table
    # there is no other way to send these with the url (in querystring) as the return url must be registered
    # and session var won't save due to redirect
    twitter_id, fb_id, forum_id, google_id = get_smids_fromuid(user.id)
    t = OauthFlowTemp.objects.filter(googleid=google_id).delete()
    temp_transfer_data = OauthFlowTemp(googleid=google_id, course_code=course_code, platform=platform, transferdata=channelIds)
    temp_transfer_data.save()

    FLOW_YOUTUBE = OAuth2WebServerFlow(
        client_id=youtube_plugin.api_config_dict['CLIENT_ID'],
        client_secret=youtube_plugin.api_config_dict['CLIENT_SECRET'],
        scope=youtube_plugin.scope,
        redirect_uri=redirecturl
    )

    authUri = FLOW_YOUTUBE.step1_get_authorize_url()
    #Redirect to REDIRECT_URI
    return HttpResponseRedirect(authUri)

def ytAuthCallback(request):

    html_response = HttpResponse()

    youtube_plugin = settings.DATAINTEGRATION_PLUGINS['YouTube']

    redirecturl= 'http://' + get_current_site(request).domain + '/dataintegration/ytAuthCallback'

    FLOW_YOUTUBE = OAuth2WebServerFlow(
        client_id=youtube_plugin.api_config_dict['CLIENT_ID'],
        client_secret=youtube_plugin.api_config_dict['CLIENT_SECRET'],
        scope=youtube_plugin.scope,
        redirect_uri=redirecturl
    )

    http = googleAuth(request, FLOW_YOUTUBE)
    user = request.user

    user_channelid = youtube_getpersonalchannel(request, http)

    t = OauthFlowTemp.objects.filter(googleid='http://www.youtube.com/channel/'+user_channelid)
    course_code = t[0].course_code
    platform = t[0].platform
    channelIds = t[0].transferdata

    ytList = youtube_plugin.perform_import(channelIds, course_code, http)

    vList = ytList[0]
    vNum = len(vList)
    commList = ytList[1]
    commNum = len(commList)
    context_dict = {"vList": vList, "vNum": vNum, "commList": commList, "commNum": commNum}

    post_smimport(course_code, platform)

    return render(request, 'dataintegration/ytresult.html', context_dict)

##############################################
# Data Extraction for YouTube
##############################################
def get_youtubechannel(request):
    youtube_plugin = settings.DATAINTEGRATION_PLUGINS['YouTube']

    redirecturl= 'http://' + get_current_site(request).domain + '/dataintegration/showyoutubechannel'

    FLOW_YOUTUBE = OAuth2WebServerFlow(
        client_id=youtube_plugin.api_config_dict['CLIENT_ID'],
        client_secret=youtube_plugin.api_config_dict['CLIENT_SECRET'],
        scope=youtube_plugin.scope,
        redirect_uri=redirecturl
    )

    authUri = FLOW_YOUTUBE.step1_get_authorize_url()
    #Redirect to REDIRECT_URI
    return HttpResponseRedirect(authUri)

def showyoutubechannel(request):

    youtube_plugin = settings.DATAINTEGRATION_PLUGINS['YouTube']

    redirecturl= 'http://' + get_current_site(request).domain + '/dataintegration/showyoutubechannel'

    FLOW_YOUTUBE = OAuth2WebServerFlow(
        client_id=youtube_plugin.api_config_dict['CLIENT_ID'],
        client_secret=youtube_plugin.api_config_dict['CLIENT_SECRET'],
        scope=youtube_plugin.scope,
        redirect_uri=redirecturl
    )

    http = googleAuth(request, FLOW_YOUTUBE)

    channel_url = youtube_getpersonalchannel(request, http)

    html_response = HttpResponse()

    if channel_url:
        html_response.write(u'<h2>Your YouTube Channel URL is: http://www.youtube.com/channel/{0}</h2>'.format(channel_url))
    else:
        html_response.write('No Channel url found. Please ensure that you are logged into YouTube and try again.')

    return html_response

def home(request):
    form = FacebookGatherForm()
    return render(request, 'dataintegration/facebook.html', {'form': form})

def refreshtwitter(request):
    html_response = HttpResponse()

    course_code = request.GET.get('course_code')
    hastags = request.GET.get('hashtags')

    tags = hastags.split(',')
    for tag in tags:
        twitter_plugin = settings.DATAINTEGRATION_PLUGINS['Twitter']
        twitter_plugin.perform_import(tag, course_code)

    post_smimport(course_code, "Twitter")

    html_response.write('Twitter Refreshed.')
    return html_response

def refreshdiigo(request):
    html_response = HttpResponse()

    diigo_plugin = settings.DATAINTEGRATION_PLUGINS['Diigo']

    course_code = request.GET.get('course_code')
    hastags = request.GET.get('tags')

    tags = hastags.split(',')
    for tag in tags:
        diigo_plugin.perform_import(tag, course_code)

    post_smimport(course_code, "Diigo")

    html_response.write('Diigo Refreshed.')
    return html_response


def refreshblog(request):
    html_response = HttpResponse()

    blog_plugin = settings.DATAINTEGRATION_PLUGINS['Blog']

    course_code = request.GET.get('course_code')
    hastags = request.GET.get('urls')

    urls = hastags.split(',')
    for url in urls:
        blog_plugin.perform_import(url, course_code)

    post_smimport(course_code, "Blog")

    html_response.write('Blog Refreshed.')
    return html_response

@api_view()
def dipluginauthomaticdata(request):
    return NotImplementedError

def dipluginauthomaticlogin(request):
    #Authomatic does not work with extra request parameters..... /sigh
    #TODO: Figure out a work around for authomatic without using request parameters... /sigh
    #todo: Idea: create temporary cache model to store params
    #todo: send req with params to utility function via jquery ajax to store into db
    #todo: get users platform/course_code/group_id by matching sm_id with that stored in tmp_db
    #todo: after retreiving required data, remove the record from db.... /sigh
    print 'request: %s' % request.GET

    if (request.GET.get('context') is not None):
        request.GET = request.GET.copy()

        state_dict = request.GET.pop('context')
        state_dict = state_dict[0]
        state_dict = json.loads(state_dict)

        print str(state_dict)

        request.session['platform'] = state_dict['platform']
        request.session['course_code'] = state_dict['course_code']
        request.session['group_id'] = state_dict['group']

    print 'Data stored in session: %s, %s, %s' % (request.session['platform'], request.session['course_code'], request.session['group_id'])

    platform = request.session['platform']

    #if (request.GET.get('platform') and
    #    request.GET.get('course_code') and
    #    request.GET.get('group') is not None):


    html_response = HttpResponse()

    #print 'Platform exists? %s' % (platform in settings.DATAINTEGRATION_PLUGINS_INCLUDEAUTHOMATIC)
    if (platform in settings.DATAINTEGRATION_PLUGINS_INCLUDEAUTHOMATIC):
        di_plugin = settings.DATAINTEGRATION_PLUGINS[platform]
        authomatic = Authomatic(di_plugin.authomatic_config_json, di_plugin.authomatic_secretkey)

        result = authomatic.login(DjangoAdapter(request, html_response), di_plugin.authomatic_config_key, report_errors=True)

        print di_plugin

        print di_plugin.authomatic_config_json

        # If there is no result, the login procedure is still pending.
        # Don't write anything to the response if there is no result!
        print result
        if result:
            # If there is result, the login procedure is over and we can write to response.
            html_response.write('<a href="..">Home</a>')

            if result.error:
                # Login procedure finished with an error.
                html_response.write('<h2>Error: {0}</h2>'.format(result.error.message))

            elif result.user:
                # Hooray, we have the user!
                # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
                # We need to update the user to get more info.
                if not (result.user.name and result.user.id):
                    result.user.update()

                # Welcome the user.
                html_response.write(u'<p>Hi {0}</p>'.format(result.user.name))
                # response.write(u'<h2>Your id is: {0}</h2>'.format(result.user.id))
                # response.write(u'<h2>Your email is: {0}</h2>'.format(result.user.email))

                # If there are credentials (only by AuthorizationProvider),
                # we can _access user's protected resources.
                if result.user.credentials:
                    group_id = request.session['group_id']
                    course_code = request.session['course_code']
                    if result.provider.name == 'fb':
                        di_plugin.perform_import(group_id, course_code, result)

                        post_smimport(course_code, "Facebook")

                        #Remove all data stored in session for this view to avoid cache issues
                        del request.session['platform']
                        del request.session['course_code']
                        del request.session['group_id']
                        html_response.write('Updating Facebook for ' + course_code)
                        #return html_response
    else:
        return html_response.write('Auth returned no Response.')

    #print html_response
    return html_response

def get_social_media_id(request):
    '''
    Gets users social media IDs for use in signup for information integration.
    :param request:
    :return:
    '''
    # TODO: Add social media functionality apart from facebook
    # We we need the response object for the adapter.
    html_response = HttpResponse()

    #Facebook endpoints break on GET variables.....
    platform = 'facebook' #request.GET.get('platform')

    if (platform in settings.DATAINTEGRATION_PLUGINS_INCLUDEAUTHOMATIC):
        di_plugin = settings.DATAINTEGRATION_PLUGINS[platform]
        authomatic = Authomatic(di_plugin.authomatic_config_json, di_plugin.authomatic_secretkey)
        result = authomatic.login(DjangoAdapter(request, html_response), di_plugin.authomatic_config_key, report_errors=True)

        # If there is no result, the login procedure is still pending.
        # Don't write anything to the response if there is no result!
        print result
        if result:
            # If there is result, the login procedure is over and we can write to response.
            #html_response.write('<a href="..">Home</a>')

            if result.error:
                # Login procedure finished with an error.
                print 'ERROR: %s' % (str(result.error))
                html_response.write('<p>Error: {0}</p>'.format(result.error.message))

            elif result.user:
                # Hooray, we have the user!

                # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
                # We need to update the user to get more info.
                if not (result.user.name and result.user.id):
                    result.user.update()

                # Welcome the user.
                # html_response.write(u'<p>Hi {0}</p>'.format(result.user.name))
                html_response.write(u'<h2>Your Facebook id is: {0}</h2>'.format(result.user.id))
        else:
            html_response.write('Auth Returned no Response.')

    return html_response

def refreshforum(request):
    html_response = HttpResponse()

    course_code = request.GET.get('course_code')
    forumurl = request.GET.get('forumurl')

    forum_plugin = settings.DATAINTEGRATION_PLUGINS['Forum']
    forum_plugin.perform_import("", course_code)

    post_smimport(course_code, "Forum")

    html_response.write('Forum Refreshed.')
    return html_response

def sendtolrs(request):
    html_response = HttpResponse()

    updateLRS()

    html_response.write('Statements Sent to LRS.')
    return html_response

def assigngroups(request):
    html_response = HttpResponse()
    course_code = request.GET.get('course_code', None)
    GroupMap.objects.filter(course_code=course_code).delete()
    assign_groups_class(course_code)
    html_response.write('Groups Assigned')
    return html_response
