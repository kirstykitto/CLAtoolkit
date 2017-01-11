import datetime
import random
import requests
from .utils import *
from functools import wraps
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseServerError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import connection
from django.db.models import Count
from django.db.models import Q
from clatoolkit.models import OfflinePlatformAuthToken, UserProfile, OauthFlowTemp, UnitOffering, UnitOfferingMembership, DashboardReflection, LearningRecord, Classification, UserClassification, GroupMap, UserPlatformResourceMap
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from xapi.models import ClientApp, UserAccessToken_LRS
from xapi.statement.xapi_settings import xapi_settings



#API endpoint to grab a list of trello boards to attach to course
@login_required
@api_view()
def get_trello_boards(request):
    user_profile = UserProfile.objects.get(user=request.user)
    trello_member_id = user_profile.trello_account_name
    token_qs = None
    try:
        token_qs = OfflinePlatformAuthToken.objects.get(user_smid=trello_member_id)
    except ObjectDoesNotExist:
        # When user smid is not found (This occurs when user hasn't registered their Trello ID yet)
        token_qs = None

    # Return error message to the client
    if token_qs is None:
        html_tags = '<p class="no-trello-id">Your Trello account is incorrect or not found.<br>'
        html_tags = html_tags + 'Register your account in Social Media Accounts update page before attaching a Trello board.<br>'
        html_tags = html_tags + '(Click your name (top right corner) - Social Media Accounts)</p>'
        return Response(('').join([html_tags]))

    token = token_qs.token
    key = os.environ.get('TRELLO_API_KEY')
    course_id = request.GET.get('course_id')
    trello_boardsList_url = 'https://api.trello.com/1/member/me/boards?key=%s&token=%s' % (key,token)
    
    r = requests.get(trello_boardsList_url)
    #print "got response %s" % r.json()
    boardsList = r.json()
    board_namesList = []
    board_namesList.append('<ul>')

    for board in boardsList:
        board_namesList.append('<li>')
        #board = json.load(board)

        #format to something nice :)
        board_name = board['name']
        board_url = board['url']
        board_id = board['id']
        html_resp = '<a href="#" class="board_choice" onclick="javascript:add_board(\''+course_id+'\',\''+board_id+'\',\'Trello\')">'+board_name+'</a>'

        board_namesList.append(html_resp)
        board_namesList.append('</li>')
    board_namesList.append('</ul>')

    return Response(('').join(board_namesList))

@login_required
@api_view()
#API endpoint to allow students to attach a board to course
def add_board_to_course(request):
    course = UnitOffering.objects.get(id=request.GET.get('course_id'))
    board_list = course.attached_trello_boards

    if board_list == '':
        new_board_list = request.GET.get('id')
    else:
        new_board_list = board_list+','+request.GET.get('id')

    course.attached_trello_boards = new_board_list
    course.save()

    trello_user_course_map = UserPlatformResourceMap(
        user=request.user, unit=course, resource_id=request.GET.get('id'), platform=xapi_settings.PLATFORM_TRELLO)
    trello_user_course_map.save()

    return Response('<b>Board successfully added to course - <a href="/dashboard/myunits/">Reload</a></b>')


def check_access(required_roles=None):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            # Check that user has correct role
            role = request.user.userprofile.role
            correct_role = False
            if role in required_roles:
                correct_role = True

            if correct_role:
                if request.method == 'POST':
                    course_code = request.POST['course_code']
                else:
                    course_code = request.GET.get('course_code')
                # Check that user is a member of the course
                unit = UnitOffering.objects.filter(code=course_code, users=request.user.id)
                if (len(unit) != 0):
                    return view(request, *args, **kwargs)
                else:
                    return HttpResponse('Access Denied - Not assigned to unit.')
            else:
                return HttpResponse('Access Denied - Incorrect Role.')
        return wrapper
    return decorator


@login_required
@api_view()
def trello_remove_board(request):
    course_id = request.GET.get('course_id')

    trello_user_course_map = None
    unit = None
    try:
        # trello_user_course_map = UserTrelloCourseBoardMap.objects.filter(user=request.user, course_code=course_code)
        trello_user_course_map = UserPlatformResourceMap.objects.filter(user=request.user, unit=course_id, 
            platform=xapi_settings.PLATFORM_TRELLO)
        unit = UnitOffering.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return HttpResponseServerError('<h2>Internal Server Error (500)</h2><p>Could not remove Trello Board.</p>')

    new_board_list = []
    same_board_list = []
    for board in unit.attached_trello_boards.split(','):
        if board != trello_user_course_map[0].resource_id:
            new_board_list.append(board)
        else:
            same_board_list.append(board)

    # Multiple users are likely to use the same Trello board. 
    # So, two or more same board IDs are likely to be found in unit.attached_trello_boards column.
    # Since we only want to delete the user's board ID, we remove one of the same board IDs from the column.
    # 
    # attached_trello_boards column only has board IDs.
    # So, we cannot identify exactly which ID is the user's when multiple same IDs exist.
    for index in range(1, len(same_board_list)):
        # Start the for loop from 1 (not 0) to remove one of the same board IDs.
        new_board_list.append(same_board_list[index])
    unit.attached_trello_boards = ','.join(new_board_list)

    unit.save()
    trello_user_course_map.delete()        
    return myunits(request)

@login_required
@api_view()
def trello_myunits_restview(request):
        #Get course code, and match it with the user to obtain the board ID for the user for their specified course.
        course_id = request.GET.get('course_id')
        trello_user_course_map = UserPlatformResourceMap.objects.filter(
            user=request.user, unit=course_id, platform=xapi_settings.PLATFORM_TRELLO)

        #If a board exists for the user and it's attached to the course
        if trello_user_course_map:
            #Get user auth token for trello
            token_qs = OfflinePlatformAuthToken.objects.filter(user_smid=request.user.userprofile.trello_account_name)

            #if the token exists, grab the board from trello on behalf of the user
            if token_qs:
                key = os.environ.get("TRELLO_API_KEY")
                http = 'https://api.trello.com/1/boards/%s?key=%s&token=%s' % (trello_user_course_map[0].resource_id, key, token_qs[0].token)
                r = requests.get(http)
                board = r.json()
                response = {'data': '<a href="'+board['url']+'""><i class="fa fa-trello" aria-hidden="true"></i>   '+board['name']+'</a> | '
                            '<a href="/dashboard/removeBoard?course_id='+course_id+'">Remove</a>', 'course_id': course_id}

                return Response(response)

        else: #Otherwise, we'll give the student the option to attach their trello board
            response = {'data': '<a href="#" onclick="javascript:get_and_link_board(\''+course_id+'\')">Attach a Trello Board to plan your Work!</a>'
                            '<div id="trello_board_display"></div>', 'course_id': course_id}
            return Response(response)


@login_required
def myunits(request):
    context = RequestContext(request)

    # Get a users memberships to unit offerings
    memberships = UnitOfferingMembership.objects.filter(user=request.user, unit__enabled=True).select_related('unit')

    role = request.user.userprofile.role
    show_dashboardnav = False
    shownocontentwarning = False
    trello_attached = not request.user.userprofile.trello_account_name == ''
    github_attached = False
    tokens = OfflinePlatformAuthToken.objects.filter(
        user_smid=request.user.userprofile.github_account_name, platform=xapi_settings.PLATFORM_GITHUB)
    if len(tokens) == 1:
        github_attached = True

    has_token_list = {}
    for membership in memberships:
        token = UserAccessToken_LRS.objects.filter(user = request.user, clientapp = membership.unit.lrs_provider)
        has_user_token = True if len(token) == 1 else False
        if len(token) > 1:
            return HttpResponseServerError('More than one access token were found.')

        app = membership.unit.lrs_provider
        has_token_list[membership.unit.code] = {'lrs': app.provider, 'has_user_token': has_user_token}

    # if student check if the student has imported data
    if role == 'Student':
        if LearningRecord.objects.filter(user=request.user).count() == 0:
            shownocontentwarning = True

    context_dict = {'title': "My Units", 'memberships': memberships, 'show_dashboardnav': show_dashboardnav,
                    'shownocontentwarning': shownocontentwarning, 'role': role,
                    'trello_attached_to_acc': trello_attached, 'has_token_list': has_token_list,
                    'github_attached': github_attached}

    return render_to_response('dashboard/myunits.html', context_dict, context)


@login_required
def dashboard(request):
    context = RequestContext(request)

    unit_id = request.GET.get('unit')
    unit = UnitOffering.objects.get(id=unit_id)

    # If the user is an admin for the course
    if UnitOfferingMembership.is_admin(request.user, unit):

        platform = request.GET.get('platform')

        title = "Activity Dashboard: %s (Platform: %s)" % (unit.code, platform)
        show_dashboardnav = True

        profiling = ""
        profiling = profiling + "| Verb Timelines %s" % (str(datetime.datetime.now()))
        posts_timeline = get_timeseries('created', platform, unit)
        shares_timeline = get_timeseries('shared', platform, unit)
        likes_timeline = get_timeseries('liked', platform, unit)
        comments_timeline = get_timeseries('commented', platform, unit)

        show_allplatforms_widgets = False
        twitter_timeline = ""
        facebook_timeline = ""
        forum_timeline = ""
        youtube_timeline = ""
        diigo_timeline = ""
        blog_timeline = ""
        github_timeline = ""
        trello_timeline = ""

        profiling = profiling + "| Platform Timelines %s" % (str(datetime.datetime.now()))
        platformclause = ""

        #TODO: This will need to change upon implementation of teaching periods

        if platform != "all":
            platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)
        else:
            twitter_timeline = get_timeseries_byplatform("Twitter", unit)
            facebook_timeline = get_timeseries_byplatform("Facebook", unit)
            forum_timeline = get_timeseries_byplatform("Forum", unit)
            youtube_timeline = get_timeseries_byplatform("YouTube", unit)
            diigo_timeline = get_timeseries_byplatform("Diigo", unit)
            blog_timeline = get_timeseries_byplatform("Blog", unit)
            github_timeline = get_timeseries_byplatform("GitHub", unit)
            trello_timeline = get_timeseries_byplatform("trello", unit)
            show_allplatforms_widgets = True

        profiling = profiling + "| Pies %s" % (str(datetime.datetime.now()))
        cursor = connection.cursor()
        cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US' as verb, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                            FROM clatoolkit_learningrecord
                            WHERE clatoolkit_learningrecord.unit_id='%s' %s
                            GROUP BY clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US';
                        """ % (unit.id, platformclause))
        result = cursor.fetchall()

        activity_pie_series = ""
        for row in result:
            activity_pie_series = activity_pie_series + "['%s',  %s]," % (row[0],row[1])

        cursor = connection.cursor()
        cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'context'->>'platform' as platform, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                            FROM clatoolkit_learningrecord
                            WHERE clatoolkit_learningrecord.unit_id='%s'
                            GROUP BY clatoolkit_learningrecord.xapi->'context'->>'platform';
                        """ % (unit.id))
        result = cursor.fetchall()

        platformactivity_pie_series = ""
        for row in result:
            platformactivity_pie_series = platformactivity_pie_series + "['%s',  %s]," % (row[0],row[1])

        #active members table
        profiling = profiling + "| Active Members %s" % (str(datetime.datetime.now()))

        p = platform if platform != "all" else None
        activememberstable = get_active_members_table(unit, p)

        profiling = profiling + "| Top Content %s" % (str(datetime.datetime.now()))
        topcontenttable = get_cached_top_content(platform, unit)
        profiling = profiling + "| End Top Content %s" % (str(datetime.datetime.now()))

        context_dict = {'profiling': profiling, 'show_dashboardnav':show_dashboardnav,
        'course_code':unit.code, 'platform':platform,
        'twitter_timeline': twitter_timeline, 'facebook_timeline': facebook_timeline, 'forum_timeline': forum_timeline,
        'youtube_timeline':youtube_timeline, 'diigo_timeline':diigo_timeline, 'blog_timeline':blog_timeline,
        'github_timeline': github_timeline, 'trello_timeline': trello_timeline,
        'show_allplatforms_widgets': show_allplatforms_widgets, 'platformactivity_pie_series': platformactivity_pie_series,
        'title': title, 'activememberstable': activememberstable, 'topcontenttable': topcontenttable,
        'activity_pie_series': activity_pie_series, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline,
        'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }

        return render_to_response('dashboard/dashboard.html', context_dict, context)

    else:
        raise PermissionDenied


@login_required
def cadashboard(request):
    context = RequestContext(request)

    platform = None
    no_topics = 3

    if request.method == 'POST':
        unit_id = request.POST['unit']
        platform = request.POST['platform']
        no_topics = int(request.POST['no_topics'])
    else:
        unit_id = request.GET.get('unit')
        platform = request.GET.get('platform')

    unit = UnitOffering.objects.get(id=unit_id)

    if UnitOfferingMembership.is_admin(request.user, unit):

        title = "Content Analysis Dashboard: %s (Platform: %s)" % (unit.code, platform)
        show_dashboardnav = True

        posts_timeline = get_timeseries('created', platform, unit)
        shares_timeline = get_timeseries('shared', platform, unit)
        likes_timeline = get_timeseries('liked', platform, unit)
        comments_timeline = get_timeseries('commented', platform, unit)

        tags = get_wordcloud(platform, unit)

        sentiments = getClassifiedCounts(platform, unit, classifier="VaderSentiment")
        coi = getClassifiedCounts(platform, unit, classifier="NaiveBayes_t1.model")

        topic_model_output, sentimenttopic_piebubblesdataset = nmf(platform, no_topics, unit, start_date=None, end_date=None)

        context_dict = {'show_dashboardnav': show_dashboardnav, 'unit': unit, 'platform': platform, 'title': title,
                        'sentiments': sentiments, 'coi': coi, 'tags': tags, 'posts_timeline': posts_timeline,
                        'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline,
                        'comments_timeline': comments_timeline, 'no_topics': no_topics,
                        'topic_model_output': topic_model_output,
                        'sentimenttopic_piebubblesdataset': sentimenttopic_piebubblesdataset}

        return render_to_response('dashboard/cadashboard.html', context_dict, context)

    else:
        raise PermissionDenied


@login_required
def snadashboard(request):
    context = RequestContext(request)

    unit_id = request.GET.get('unit')
    unit = UnitOffering.objects.get(id=unit_id)

    if UnitOfferingMembership.is_admin(request.user, unit):

        platform = request.GET.get('platform')

        title = "SNA Dashboard: {} {} (Platform: {})".format(unit.code, unit.name, platform)
        show_dashboardnav = True

        posts_timeline = get_timeseries('created', platform, unit)
        shares_timeline = get_timeseries('shared', platform, unit)
        likes_timeline = get_timeseries('liked', platform, unit)
        comments_timeline = get_timeseries('commented', platform, unit)

        sna_json = sna_buildjson(platform, unit, relationshipstoinclude="'mentioned','liked','shared','commented'")
        #sna_neighbours = getNeighbours(sna_json)
        centrality = getCentrality(sna_json)
        context_dict = {'show_dashboardnav': show_dashboardnav, 'unit': unit, 'platform': platform, 'title': title,
                        'sna_json': sna_json, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline,
                        'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline,
                        'centrality': centrality}

        return render_to_response('dashboard/snadashboard.html', context_dict, context)

    else:
        raise PermissionDenied


@check_access(required_roles=['Staff'])
@login_required
def pyldavis(request):
    context = RequestContext(request)
    if request.method == 'POST':
        course_code = request.POST['course_code']
        platform = request.POST['platform']
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date', None)
    else:
        course_code = request.GET.get('course_code')
        platform = request.GET.get('platform')
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

    pyLDAVis_json = get_LDAVis_JSON(platform, 5, course_code, start_date=start_date, end_date=end_date)
    context_dict = {'title': "Topic Model", 'pyLDAVis_json': pyLDAVis_json}

    return render_to_response('dashboard/pyldavis.html', context_dict, context)

@check_access(required_roles=['Staff'])
@login_required
def studentdashboard(request):
    context = RequestContext(request)

    course_code = None
    platform = None
    username = None

    course_code = request.GET.get('course_code')
    platform = request.GET.get('platform')
    username = request.GET.get('username')
    username_platform = request.GET.get('username_platform')

    #userid = get_smids_fromusername(username)
    twitter_id, fb_id, forum_id, github_id, trello_id, blog_id, diigo_id = get_smids_fromusername(username)
    sm_usernames_dict = {'Twitter': twitter_id, 'Facebook': fb_id, 'Forum': forum_id}
    sm_usernames = [twitter_id, fb_id, forum_id]

    sm_usernames_str = ','.join("'{0}'".format(x) for x in sm_usernames)

    title = "Student Dashboard: %s, (Twitter: %s, Facebook: %s, Forum: %s)" % (course_code, twitter_id, fb_id, forum_id)

    if course_code == 'IFN614':
            title = "Student Dashboard: %s, (Twitter: %s, Blog: %s)" % (course_code, twitter_id, blog_id)


    show_dashboardnav = True

    #print "Verb timelines", datetime.datetime.now()
    posts_timeline = get_timeseries('created', platform, course_code, username=username)
    shares_timeline = get_timeseries('shared', platform, course_code, username=username)
    likes_timeline = get_timeseries('liked', platform, course_code, username=username)
    comments_timeline = get_timeseries('commented', platform, course_code, username=username)

    #print "Activity by Platform", datetime.datetime.now()
    cursor = connection.cursor()
    #if course_code == 'IFN614':
    #    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US' as verb, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
    #                        FROM clatoolkit_learningrecord
    #                        WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username='%s' AND clatoolkit_learningrecord.datetimestamp > '%s'
    #                        GROUP BY clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US';
    #                """ % (course_code, username, '29-06-2016'))
    #else:
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US' as verb, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                    FROM clatoolkit_learningrecord
                    WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username='%s'
                    GROUP BY clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US';
            """ % (course_code, username))
    result = cursor.fetchall()

    activity_pie_series = ""
    for row in result:
        activity_pie_series = activity_pie_series + "['%s',  %s]," % (row[0],row[1])

    show_allplatforms_widgets = False
    twitter_timeline = ""
    facebook_timeline = ""
    forum_timeline = ""
    youtube_timeline = ""
    diigo_timeline = ""
    blog_timeline = ""
    github_timeline = ""
    trello_timeline = ""

    #print "Platform timelines", datetime.datetime.now()
    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)
    else:
        twitter_timeline = get_timeseries_byplatform("Twitter", course_code, username)
        facebook_timeline = get_timeseries_byplatform("Facebook", course_code, username)
        forum_timeline = get_timeseries_byplatform("Forum", course_code, username)
        youtube_timeline = get_timeseries_byplatform("YouTube", course_code, username)
        diigo_timeline = get_timeseries_byplatform("Diggo", course_code, username)
        blog_timeline = get_timeseries_byplatform("Blog", course_code, username)
        github_timeline = get_timeseries_byplatform("GitHub", course_code)
        trello_timeline = get_timeseries_byplatform("trello", course_code)

        show_allplatforms_widgets = True

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'context'->>'platform' as platform, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username='%s'
                        GROUP BY clatoolkit_learningrecord.xapi->'context'->>'platform';
                    """ % (course_code, username))
    result = cursor.fetchall()

    platformactivity_pie_series = ""
    for row in result:
        platformactivity_pie_series = platformactivity_pie_series + "['%s',  %s]," % (row[0],row[1])

    #print "Top Content", datetime.datetime.now()
    topcontenttable = get_top_content_table(platform, course_code, username=username)

    #print "SNA", datetime.datetime.now()
    if course_code == 'IFN614':
        sna_json = sna_buildjson(platform, course_code, start_date='15-06-2016', end_date='20-12-2016', relationshipstoinclude="'mentioned','liked','shared','commented'")
    else:
        sna_json = sna_buildjson(platform, course_code, relationshipstoinclude="'mentioned','liked','shared','commented'")


    #print "Word Cloud", datetime.datetime.now()
    tags = get_wordcloud(platform, course_code, username=username)

    sentiments = getClassifiedCounts(platform, course_code, username=username, classifier="VaderSentiment")

    coi = getClassifiedCounts(platform, course_code, username=username, classifier="nb_"+course_code+"_"+platform+".model")


    context_dict = {'show_allplatforms_widgets': show_allplatforms_widgets, 
    'twitter_timeline': twitter_timeline, 'facebook_timeline': facebook_timeline, 
    'forum_timeline':forum_timeline, 'youtube_timeline':youtube_timeline, 'diigo_timeline':diigo_timeline, 
    'blog_timeline':blog_timeline, 'github_timeline': github_timeline, 'trello_timeline': trello_timeline,
    'platformactivity_pie_series':platformactivity_pie_series, 'show_dashboardnav':show_dashboardnav, 
    'course_code':course_code, 'platform':platform, 'title': title, 'course_code':course_code, 
    'platform':platform, 'username':username, 'sna_json': sna_json,  'tags': tags, 
    'topcontenttable': topcontenttable, 'activity_pie_series': activity_pie_series, 
    'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 
    'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline, 
    'sentiments': sentiments, 'coi': coi }

    return render_to_response('dashboard/studentdashboard.html', context_dict, context)

@check_access(required_roles=['Student'])
@login_required
def mydashboard(request):
    context = RequestContext(request)

    course_code = None
    platform = None
    user = request.user

    if request.method == 'POST':
        course_code = request.POST['course_code']
        platform = request.POST['platform']

        # save reflection
        reflectiontext = request.POST['reflectiontext']
        rating = request.POST['rating']
        reflect = DashboardReflection(strategy = reflectiontext, rating = rating, user = user)
        reflect.save()

    else:
        course_code = request.GET.get('course_code')
        platform = request.GET.get('platform')
        #username = request.GET.get('username')

    unit = UnitOffering.objects.get(code = course_code)

    # TODO: What are these for?? weren't used...
    # twitter_id, fb_id, forum_id, github_id, trello_id, blog_id, diigo_id = get_smids_fromuid(uid)
    # twitter_id = user.userprofile.twitter_id
    # fb_id = user.userprofile.fb_id
    # forum_id = user.userprofile.forum_id
    # sm_usernames = [twitter_id, fb_id, forum_id]
    # sm_usernames_str = ','.join("'{0}'".format(x) for x in sm_usernames)

    title = "Student Dashboard: %s, %s" % (course_code, user.username)
    show_dashboardnav = True

    # Activity Time line data (verbs and platform)
    timeline_data = get_timeline_data(unit, user)
    platform_timeline_data = get_platform_timeline_data(unit, user)

    # A flag for showing a platform activity time series and pie chart
    show_allplatforms_widgets = True
    if platform != "all":
        show_allplatforms_widgets = False

    # Get the number of verbs and platforms
    activity_pie_series = get_pie_series(unit, 'verb', user.id)
    platformactivity_pie_series = get_pie_series(unit, 'platform', user.id)
    
    # Word cloud tags
    tags = get_wordcloud(platform, unit, user = user)
    # Sentiments pie chart
    sentiments = getClassifiedCounts(platform, unit, user = user, classifier="VaderSentiment")
    # Community of Inquiry
    coi = getClassifiedCounts(platform, unit, user = user, classifier="nb_"+course_code+"_"+platform+".model")
    # Dashboard reflection
    reflections = DashboardReflection.objects.filter(user = user)
    
    # TODO: Fix get_timeseries() method 
    # posts_timeline = get_timeseries('created', platform, course_code, username=username)
    # shares_timeline = get_timeseries('shared', platform, course_code, username=username)
    # likes_timeline = get_timeseries('liked', platform, course_code, username=username)
    # comments_timeline = get_timeseries('commented', platform, course_code, username=username)

    # cursor = connection.cursor()
    # cursor.execute("""SELECT clatoolkit_learningrecord.verb as verb, count(clatoolkit_learningrecord.verb) as counts
    #                     FROM clatoolkit_learningrecord
    #                     WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username='%s'
    #                     GROUP BY clatoolkit_learningrecord.verb;
    #                 """ % (course_code, username))
    # result = cursor.fetchall()

    # activity_pie_series = ""
    # for row in result:
    #     activity_pie_series = activity_pie_series + "['%s',  %s]," % (row[0],row[1])

    # show_allplatforms_widgets = False
    # twitter_timeline = ""
    # facebook_timeline = ""
    # forum_timeline = ""
    # youtube_timeline = ""
    # diigo_timeline = ""
    # blog_timeline = ""

    # platformclause = ""
    # if platform != "all":
    #     platformclause = " AND clatoolkit_learningrecord.platform='%s'" % (platform)
    # else:
    #     twitter_timeline = get_timeseries_byplatform("Twitter", course_code, username)
    #     facebook_timeline = get_timeseries_byplatform("Facebook", course_code, username)
    #     forum_timeline = get_timeseries_byplatform("Forum", course_code, username)
    #     youtube_timeline = get_timeseries_byplatform("YouTube", course_code, username)
    #     diigo_timeline = get_timeseries_byplatform("Diigo", course_code, username)
    #     blog_timeline = get_timeseries_byplatform("Blog", course_code, username)
    #     show_allplatforms_widgets = True

    # cursor = connection.cursor()
    # cursor.execute("""SELECT clatoolkit_learningrecord.platform as platform, count(clatoolkit_learningrecord.verb) as counts
    #                     FROM clatoolkit_learningrecord
    #                     WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username='%s'
    #                     GROUP BY clatoolkit_learningrecord.platform;
    #                 """ % (course_code, username))
    # result = cursor.fetchall()

    # platformactivity_pie_series = ""
    # for row in result:
    #     platformactivity_pie_series = platformactivity_pie_series + "['%s',  %s]," % (row[0],row[1])

    # #topcontenttable = get_top_content_table(platform, course_code, username=username)

    # sna_json = sna_buildjson(platform, course_code, relationshipstoinclude="'mentioned','liked','shared','commented'")
    # centrality = getCentrality(sna_json)
    # tags = get_wordcloud(platform, unit, username=username)

    # sentiments = getClassifiedCounts(platform, unit, username=username, classifier="VaderSentiment")
    # coi = getClassifiedCounts(platform, unit, username=username, classifier="nb_"+course_code+"_"+platform+".model")

    # reflections = DashboardReflection.objects.filter(username=username)
    # context_dict = {'show_allplatforms_widgets': show_allplatforms_widgets, 
    #     'forum_timeline': forum_timeline, 'twitter_timeline': twitter_timeline, 
    #     'facebook_timeline': facebook_timeline, 'youtube_timeline': youtube_timeline, 
    #     'diigo_timeline':diigo_timeline, 'blog_timeline':blog_timeline, 
    #     'platformactivity_pie_series':platformactivity_pie_series, 
    #     'show_dashboardnav':show_dashboardnav, 'course_code':course_code, 
    #     'platform':platform, 'title': title, 'course_code':course_code, 'platform':platform, 
    #     'username':username, 'reflections':reflections, 'sna_json': sna_json,
    #     'tags': tags, 'activity_pie_series': activity_pie_series, 'posts_timeline': posts_timeline, 
    #     'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 
    #     'comments_timeline': comments_timeline, 'sentiments': sentiments, 'coi': coi,
    #     'centrality': centrality
    # }
    context_dict = {
        'title': title, 'course_code':course_code, 'username': user.username,
        'posts_timeline': timeline_data['posts'], 'shares_timeline': timeline_data['shares'], 
        'likes_timeline': timeline_data['likes'], 'comments_timeline': timeline_data['comments'],
        'activity_pie_series': activity_pie_series,
        'platformactivity_pie_series':platformactivity_pie_series, 
        'show_allplatforms_widgets': show_allplatforms_widgets,
        'platform':platform, 'tags': tags, 'sna_json': [], 'centrality': [],
        'sentiments': sentiments, 'coi': coi, 'reflections':reflections
        }

    return render_to_response('dashboard/mydashboard.html', context_dict, context)


@login_required
def myclassifications(request):
    context = RequestContext(request)

    course_code = None
    platform = None

    user = request.user
    username = user.username
    uid = user.id

    course_code = request.GET.get('course_code')
    platform = request.GET.get('platform')

    #user_profile = UserProfile.objects.filter(user=user)

    group_id_seed = GroupMap.objects.filter(userId=user, course_code=course_code).values_list('groupId')

    inner_q = UserClassification.objects.filter(username=username).values_list('classification_id')
    #Need to add unique identifier to models to distinguish between classes
    #xapistatement__username=username,
    classifier_name = "nb_%s_%s.model" % (course_code,platform)
    classifications_list = list(Classification.objects.filter(classifier=classifier_name).exclude(id__in = inner_q))

    if len(group_id_seed)>0:
        random.seed(group_id_seed)
        random.shuffle(classifications_list)
    else:
        random.seed()
        random.shuffle(classifications_list)

    context_dict = {'course_code':course_code, 'platform':platform, 'title': "Community of Inquiry Classification", 'username':username, 'uid':uid, 'classifications': classifications_list }
    return render_to_response('dashboard/myclassifications.html', context_dict, context)


@login_required
def ccadashboard(request):
    context = RequestContext(request)

    course_code = request.GET.get('course_code')
    platform = request.GET.get('platform')

    title = "CCA Dashboard: %s (Platform: %s)" % (course_code, platform)
    
    """
    show_dashboardnav = True

    posts_timeline = get_timeseries('created', platform, course_code)
    shares_timeline = get_timeseries('shared', platform, course_code)
    likes_timeline = get_timeseries('liked', platform, course_code)
    comments_timeline = get_timeseries('commented', platform, course_code)

    sna_json = sna_buildjson(platform, course_code, relationshipstoinclude="'mentioned','liked','shared','commented'")
    centrality = getCentrality(sna_json)
    context_dict = {
        'show_dashboardnav':show_dashboardnav,'course_code':course_code, 'platform':platform, 
        'title': title, 'sna_json': sna_json, 'posts_timeline': posts_timeline, 
        'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline,
        'centrality': centrality
    }
    """
    context_dict = {'course_code':course_code, 'platform':platform, 'title': title, }
    
    return render_to_response('dashboard/ccadashboard.html', context_dict, context)


@login_required
def ccadata(request):

    # print request.GET.get('course_code')
    # print request.GET.get('platform')

    result = getCCAData(request.user, request.GET.get('course_code'), request.GET.get('platform'))
    
    #print result

    response = JsonResponse(result, status=status.HTTP_200_OK)

    return response


@login_required
def get_platform_timeseries_data(request):

    context = RequestContext(request)
    # platform = request.GET.get('platform')
    platform_names = []

    # Should all platform be shown in timeseries? or ones in the unit?
    platform_names = ["Twitter", "Facebook", "Forum", "YouTube", "Diigo", "Blog", "trello", "GitHub"]
    # if request.GET.get('platform') is None:
    #     platform_names = ["Twitter", "Facebook", "Forum", "YouTube", "Diigo", "Blog", "trello", "GitHub"]
    # else:
    #     # TODO: Enable this code if needed. Not tested.
    #     platform_names = request.GET.get('platform').split(',')

    val = get_platform_timeseries_dataset(request.GET.get('course_code'), platform_names = platform_names)
    # return HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
    response = JsonResponse(val, status=status.HTTP_200_OK)
    return response


@login_required
def get_platform_activities(request):
    context = RequestContext(request)
    # platform = request.GET.get('platform')
    platform_names = []
    if request.GET.get('platform') is not None:
        # TODO: Enable this code if needed. Not tested.
        platform_names = request.GET.get('platform').split(',')

    val = get_activity_dataset(request.GET.get('course_code'), platform_names)
    response = JsonResponse(val, status=status.HTTP_200_OK)
    return response


def get_user_acitivities(request):
    platform_names = request.GET.get('platform').split(',')
    val = get_user_acitivities_dataset(request.GET.get('course_code'), platform_names)
    response = JsonResponse(val, status=status.HTTP_200_OK)
    return response


@login_required
def get_all_repos(request):
    tokens = OfflinePlatformAuthToken.objects.filter(
        user_smid=request.user.userprofile.github_account_name, platform=xapi_settings.PLATFORM_GITHUB)
    if len(tokens) == 0 or len(tokens) > 1:
        return []

    val = get_all_reponames(tokens[0].token)
    return JsonResponse(val, status=status.HTTP_200_OK)


@login_required
def add_repo_to_course(request):
    course_id = request.GET.get('course_id')
    course = UnitOffering.objects.get(id=course_id)
    repo_name = request.GET.get('repo')
    ret = {'result': 'success'}

    resource_map = UserPlatformResourceMap.objects.filter(
        user=request.user, unit=course_id, platform=xapi_settings.PLATFORM_GITHUB)
    # If the same record exist, update the repository name
    if len(resource_map) == 1:
        resource_map[0].resource_id = repo_name
        resource_map[0].save()
    elif len(resource_map) > 1:
        # When more than one records were found (Usually this doesn't happen)
        ret = {'result': 'error', 'message': 'More than one records were found. Could not update repository name.'}
    else:
        # Add a new record
        resource_map = UserPlatformResourceMap(
            user=request.user, unit=course, resource_id=repo_name, platform=xapi_settings.PLATFORM_GITHUB)
        resource_map.save()

    return JsonResponse(ret, status=status.HTTP_200_OK)


@login_required
def get_github_attached_repo(request):
    course_id = request.GET.get('course_id')
    if course_id is None or course_id == '':
        return JsonResponse({'result': 'error', 'message': 'Course ID not found.'}, status=status.HTTP_200_OK)

    resource_map = UserPlatformResourceMap.objects.filter(
        user=request.user, unit=course_id, platform=xapi_settings.PLATFORM_GITHUB)

    if len(resource_map) == 0:
        return JsonResponse({'result': 'error', 'message': 'No records found.'}, status=status.HTTP_200_OK)

    resource = resource_map[0]
    gh_settings = settings.DATAINTEGRATION_PLUGINS[xapi_settings.PLATFORM_GITHUB]
    obj = OrderedDict([
        ('result', 'success'),
        ('name', resource.resource_id),
        ('url', gh_settings.platform_url + resource.resource_id),
    ])

    return JsonResponse(obj, status=status.HTTP_200_OK)


@login_required
def remove_attached_repo(request):
    course_id = request.GET.get('course_id')
    if course_id is None or course_id == '':
        return JsonResponse({'result': 'error', 'message': 'Course ID not found.'}, status=status.HTTP_200_OK)

    resource_map = UserPlatformResourceMap.objects.filter(
        user=request.user, unit=course_id, platform=xapi_settings.PLATFORM_GITHUB)
    if len(resource_map) > 1:
        return JsonResponse({'result': 'error', 'message': 'More than one records were found.'}, status=status.HTTP_200_OK)

    resource_map.delete()
    ret = {'result': 'success'}
    return JsonResponse(ret, status=status.HTTP_200_OK)


@login_required
def get_github_contribution(request):
    # Get all issues and issues that each user was assigned to.
    course_code = request.GET.get('course_code')
    contribution = get_issue_list(course_code)
    
    return JsonResponse(contribution, status=status.HTTP_200_OK)
