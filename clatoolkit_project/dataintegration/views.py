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
from clatoolkit.models import UnitOffering, DashboardReflection, LearningRecord, SocialRelationship, CachedContent
from django.db import connection
import dateutil.parser
from dashboard.utils import *

### YouTube Integration ###
"""
from django.shortcuts import render
from django.http import HttpResponseRedirect
from oauth2client.client import OAuth2WebServerFlow
import httplib2
from apiclient.discovery import build
"""
from dataintegration.googleLib import *

courseCode = None
channelIds = None
#videoIds = None
courseId = None


##############################################
# Data Extraction for YouTube
##############################################
def refreshyoutube(request):
    global courseCode
    global channelIds
    global courseId
    courseCode = request.GET.get('course_code')
    channelIds = request.GET.get('channelIds')
    #videoIds = request.GET.get('videoIds')
    courseId = request.GET.get('course_id')

    authUri = FLOW_YOUTUBE.step1_get_authorize_url()
    #Redirect to REDIRECT_URI
    return HttpResponseRedirect(authUri)


##############################################
# Callback method from OAuth
##############################################
def ytAuthCallback(request):
    #Authenticate 
    http = googleAuth(request, FLOW_YOUTUBE)
    #Store extracted data into LRS
    ytList = injest_youtube(request, courseCode, channelIds, http, courseId)

    vList = ytList[0]
    vNum = len(vList)
    commList = ytList[1]
    commNum = len(commList)
    context_dict = {"vList": vList, "vNum": vNum, "commList": commList, "commNum": commNum}
    return render(request, 'dataintegration/ytresult.html', context_dict)



CONFIG = {
    # Auth information for Facebook App
    'fb': {
        'class_': oauth2.Facebook,

        'consumer_key': '',
        'consumer_secret': '',

        'scope': ['user_about_me', 'email', 'user_groups'],
    },
}

authomatic = Authomatic(CONFIG, '')

def home(request):
    form = FacebookGatherForm()
    return render(request, 'dataintegration/facebook.html', {'form': form})

def refreshtwitter(request):
    html_response = HttpResponse()

    course_code = request.GET.get('course_code')
    hastags = request.GET.get('hashtags')

    #t = LearningRecord.objects.filter(platform='Twitter',course_code=course_code).delete()
    #LearningRecord.objects.all().delete()
    #SocialRelationship.objects.all().delete()

    tags = hastags.split(',')
    for tag in tags:
        injest_twitter(tag, course_code)

    top_content = get_top_content_table("Twitter", course_code)
    active_content = get_active_members_table("Twitter", course_code)
    cached_content, created = CachedContent.objects.get_or_create(course_code=course_code, platform="Twitter")
    cached_content.htmltable = top_content
    cached_content.activitytable = active_content
    cached_content.save()

    html_response.write('Twitter Refreshed.')
    return html_response

def login(request, group_id):
    # We we need the response object for the adapter.
    html_response = HttpResponse()

    result = authomatic.login(DjangoAdapter(request, html_response), 'fb')

    # If there is no result, the login procedure is still pending.
    # Don't write anything to the response if there is no result!
    if result:
        # If there is result, the login procedure is over and we can write to response.
        html_response.write('<a href="..">Home</a>')

        if result.error:
            # Login procedure finished with an error.
            html_response.write('<h2>Error: {0}</h2>'.format(result.error.message))

        elif result.user:
            # Hooray, we have the user!
            #course_code = request.GET.get('course_code')
            #platform = request.GET.get('platform')
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

                # Each provider has it's specific API.
                if result.provider.name == 'fb':
                    # Construct Facebook group Graph API call
                    #group_id = request.GET.get('group_id')

                    url = 'https://graph.facebook.com/'+group_id+'/feed'
                    unit_offering = UnitOffering.objects.filter(facebook_groups=group_id) #request.GET.get('course_code')
                    course_code = unit_offering[0].code
                    # Access user's protected resource.
                    access_response = result.provider.access(url)
                    #print access_response
                    #print access_response.data.get('data')
                    #fb_json = json.loads(access_response.data.get('data'))
                    #pprint(access_response.data.get('data'))
                    fb_feed = access_response.data.get('data')
                    paging = access_response.data.get('paging')
                    #pprint(paging)
                    #pprint(fb_json)
                    #t = LearningRecord.objects.filter(platform='Facebook',course_code=course_code).delete()
                    injest_facebook(fb_feed, paging, course_code)
                    #injest_twitter("#clatest", "cla101")
                    top_content = get_top_content_table("Facebook", course_code)
                    active_content = get_active_members_table("Facebook", course_code)
                    cached_content, created = CachedContent.objects.get_or_create(course_code=course_code, platform="Facebook")
                    cached_content.activitytable = active_content
                    cached_content.htmltable = top_content
                    cached_content.save()
                    html_response.write('Updating Facebook for ' + course_code)

    else:
        html_response.write('Auth Returned no Response.')

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

    result = authomatic.login(DjangoAdapter(request, html_response), 'fb')


    # If there is no result, the login procedure is still pending.
    # Don't write anything to the response if there is no result!
    if result:
        # If there is result, the login procedure is over and we can write to response.
        #html_response.write('<a href="..">Home</a>')

        if result.error:
            # Login procedure finished with an error.
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

    #t = LearningRecord.objects.filter(platform='Forum').delete()

    ingest_forum(forumurl, course_code)

    top_content = get_top_content_table("Forum", course_code)
    active_content = get_active_members_table("Forum", course_code)
    cached_content, created = CachedContent.objects.get_or_create(course_code=course_code, platform="Forum")
    cached_content.htmltable = top_content
    cached_content.activitytable = active_content
    cached_content.save()

    html_response.write('Forum Refreshed.')
    return html_response

def sendtolrs(request):
    html_response = HttpResponse()

    updateLRS()

    html_response.write('Statements Sent to LRS.')
    return html_response

def updatelearningrecords(request):
    html_response = HttpResponse()

    cursor = connection.cursor()
    cursor.execute("""
        SELECT clatoolkit_learningrecord.id, clatoolkit_learningrecord.xapi->'object'->'definition'->'name'->>'en-US', clatoolkit_learningrecord.xapi->'timestamp', clatoolkit_learningrecord.username, clatoolkit_learningrecord.parentusername, clatoolkit_learningrecord.platform
        FROM clatoolkit_learningrecord
    """)
    result = cursor.fetchall()

    for row in result:
        id = row[0]
        message = row[1]
        datetimestamp = row[2]
        platform = row[5]
        username = row[3] #get_username_fromsmid(row[3], platform)
        #print "parent smid", row[4]
        parentusername = "" #get_username_fromsmid(row[4], platform)
        #print "parent username", parentusername
        if row[4]=="DennisMitchell":
            parentusername = ""
        else:
            parentusername = row[4]
        obj = LearningRecord.objects.get(pk=id)
        obj.message = message
        obj.username = username
        obj.parentusername = parentusername
        obj.datetimestamp = dateutil.parser.parse(datetimestamp)
        obj.save()

    html_response.write('Local LRS Updated.')
    return html_response


def insertsocialrelationships(request):
    html_response = HttpResponse()

    # Rebuild Relationships
    SocialRelationship.objects.filter().delete()

    sql = """
            SELECT clatoolkit_learningrecord.username, clatoolkit_learningrecord.verb, obj, clatoolkit_learningrecord.platform, clatoolkit_learningrecord.datetimestamp, clatoolkit_learningrecord.message, clatoolkit_learningrecord.course_code, clatoolkit_learningrecord.verb, clatoolkit_learningrecord.platformid
            FROM   clatoolkit_learningrecord, json_array_elements(clatoolkit_learningrecord.xapi->'context'->'contextActivities'->'other') obj
          """
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for row in result:
        #print row
        dict = row[2]
        tag = dict["definition"]["name"]["en-US"]
        if tag.startswith('@'): # hastags are also returned in query and need to be filtered out
            socialrelationship = SocialRelationship()
            socialrelationship.fromusername = row[0] #get_username_fromsmid(row[0], row[3])
            socialrelationship.tousername = get_username_fromsmid(tag[1:], row[3]) #remove @symbol
            socialrelationship.message = row[5]
            socialrelationship.datetimestamp = row[4]
            socialrelationship.platform = row[3]
            socialrelationship.verb = "mentioned"
            socialrelationship.platformid = row[8]
            socialrelationship.course_code = row[6]
            socialrelationship.save()
            print row[3]

    #get all statements with platformparentid
    sql = """
            SELECT clatoolkit_learningrecord.username, clatoolkit_learningrecord.parentusername, clatoolkit_learningrecord.verb, clatoolkit_learningrecord.platform, clatoolkit_learningrecord.platformid, clatoolkit_learningrecord.message, clatoolkit_learningrecord.datetimestamp, clatoolkit_learningrecord.course_code
            FROM clatoolkit_learningrecord
            WHERE COALESCE(clatoolkit_learningrecord.platformparentid, '') != ''
          """

    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for row in result:

            socialrelationship = SocialRelationship()
            socialrelationship.fromusername = row[0] #get_username_fromsmid(row[0], row[3])
            socialrelationship.tousername = row[1] #get_username_fromsmid(row[1], row[3])
            socialrelationship.message = row[5]
            socialrelationship.datetimestamp = row[6]
            socialrelationship.platform = row[3]
            socialrelationship.verb = row[2]
            socialrelationship.platformid = row[4]
            socialrelationship.course_code = row[7]
            socialrelationship.save()

    html_response.write('Social Relationships Updated.')
    return html_response
