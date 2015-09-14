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
from clatoolkit.models import UnitOffering, DashboardReflection, LearningRecord, CachedContent

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

    tags = hastags.split(',')
    for tag in tags:
        injest_twitter(tag, course_code)

    top_content = get_top_content_table("Twitter", course_code)
    cached_content, created = CachedContent.objects.get_or_create(course_code=course_code, platform="Twitter")
    cached_content.htmltable = top_content
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
                    cached_content, created = CachedContent.objects.get_or_create(course_code=course_code, platform="Facebook")
                    cached_content.htmltable = top_content
                    cached_content.save()
                    html_response.write('Updating Facebook for ' + course_code)
                    '''
                    if access_response.status == 200:
                        # Parse response.
                        data = access_response.data.get('data')
                        paging = access_response.data.get('paging')
                        error = access_response.data.get('error')
                        if error:
                            html_response.write(u'Error: {0}!'.format(error))
                        elif data:
                            #result = send_data_to_lrs.delay(data, paging, html_response)
                            send_data_to_lrs(data, paging, html_response)
                            #print result.id
                            #html_response.write('<p>Data is being collected from the Facebook Page with an ID of ' + group_id + '</p>')
                            #html_response.write('<p>View your task status <a href="http://localhost:5555/'
                            #                    'task/'+result.id+'">here.</a></p>')
                            html_response.write('<p>Data was collected from the Facebook Page with an ID of ' + group_id + '</p>')

                    else:
                        html_response.write('Unknown error<br />')
                        html_response.write(u'Status: {0}'.format(html_response.status))
                    '''
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

    ingest_forum(forumurl, course_code)

    top_content = get_top_content_table("Forum", course_code)
    cached_content, created = CachedContent.objects.get_or_create(course_code=course_code, platform="Forum")
    cached_content.htmltable = top_content
    cached_content.save()

    html_response.write('Forum Refreshed.')
    return html_response
