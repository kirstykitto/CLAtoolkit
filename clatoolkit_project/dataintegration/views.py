# example/simple/views.py
from __future__ import absolute_import

from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from authomatic import Authomatic
from authomatic.adapters import DjangoAdapter
from authomatic.providers import oauth2

from django.template import RequestContext

from dataintegration.tasks import *
from .forms import FacebookGatherForm
#from dataintegration.forms import UserForm, UserProfileForm
import json
from pprint import pprint

CONFIG = {
    # Auth information for Facebook App
    'fb': {
        'class_': oauth2.Facebook,

        'consumer_key': '1409411262719592',
        'consumer_secret': '8fbbb8f44a8b3e68302e2d8fb7a5ecf3',

        'scope': ['user_about_me', 'email', 'user_groups'],
    },
}

authomatic = Authomatic(CONFIG, 'lamksdlkm213213kl5n521234lkn4231')

def home(request):
    form = FacebookGatherForm()
    return render(request, 'dataintegration/facebook.html', {'form': form})

def refreshtwitter(request):
    html_response = HttpResponse()
    t = LearningRecord.objects.filter(platform='Twitter').delete()
    injest_twitter("#clatest", "cla101")
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
                    url = 'https://graph.facebook.com/'+group_id+'/feed'

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
                    t = LearningRecord.objects.filter(platform='Facebook').delete()
                    injest_facebook(fb_feed, paging, "cla101")
                    #injest_twitter("#clatest", "cla101")
                    html_response.write('....Check console')
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

'''
def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()


    # Render the template depending on the context.
    return render_to_response(
        'dataintegration/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)
'''
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
        html_response.write('<a href="..">Home</a>')

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
