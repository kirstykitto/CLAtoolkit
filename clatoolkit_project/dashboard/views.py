from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.db import connection
from utils import *
from clatoolkit.models import UnitOffering, DashboardReflection, LearningRecord
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from functools import wraps

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
def myunits(request):
    context = RequestContext(request)
    # Only get units that the user is assigned to to
    units = UnitOffering.objects.filter(users=request.user)
    role = request.user.userprofile.role

    show_dashboardnav = False

    context_dict = {'title': "My Units", 'units': units, 'show_dashboardnav':show_dashboardnav, 'role': role}

    return render_to_response('dashboard/myunits.html', context_dict, context)

@check_access(required_roles=['Staff'])
@login_required
def dashboard(request):
    context = RequestContext(request)

    course_code = request.GET.get('course_code')
    platform = request.GET.get('platform')

    title = "Activity Dashboard: %s (Platform: %s)" % (course_code, platform)
    show_dashboardnav = True

    posts_timeline = get_timeseries('created', platform, course_code)
    shares_timeline = get_timeseries('shared', platform, course_code)
    likes_timeline = get_timeseries('liked', platform, course_code)
    comments_timeline = get_timeseries('commented', platform, course_code)

    show_allplatforms_widgets = False
    twitter_timeline = ""
    facebook_timeline = ""

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)
    else:
        twitter_timeline = get_timeseries_byplatform("Twitter", course_code)
        facebook_timeline = get_timeseries_byplatform("Facebook", course_code)
        show_allplatforms_widgets = True

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US' as verb, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s' %s
                        GROUP BY clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US';
                    """ % (course_code, platformclause))
    result = cursor.fetchall()

    activity_pie_series = ""
    for row in result:
        activity_pie_series = activity_pie_series + "['%s',  %s]," % (row[0],row[1])

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'context'->>'platform' as platform, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s'
                        GROUP BY clatoolkit_learningrecord.xapi->'context'->>'platform';
                    """ % (course_code))
    result = cursor.fetchall()

    platformactivity_pie_series = ""
    for row in result:
        platformactivity_pie_series = platformactivity_pie_series + "['%s',  %s]," % (row[0],row[1])

    #active members table
    activememberstable = get_active_members_table(platform, course_code)

    topcontenttable = get_top_content_table(platform, course_code)

    context_dict = {'show_dashboardnav':show_dashboardnav, 'course_code':course_code, 'platform':platform, 'twitter_timeline': twitter_timeline, 'facebook_timeline': facebook_timeline, 'show_allplatforms_widgets': show_allplatforms_widgets, 'platformactivity_pie_series': platformactivity_pie_series,  'title': title, 'activememberstable': activememberstable, 'topcontenttable': topcontenttable, 'activity_pie_series': activity_pie_series, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }

    return render_to_response('dashboard/dashboard.html', context_dict, context)

@check_access(required_roles=['Staff'])
@login_required
def cadashboard(request):
    context = RequestContext(request)

    course_code = request.GET.get('course_code')
    platform = request.GET.get('platform')

    title = "Content Analysis Dashboard: %s (Platform: %s)" % (course_code, platform)
    show_dashboardnav = True

    posts_timeline = get_timeseries('created', platform, course_code)
    shares_timeline = get_timeseries('shared', platform, course_code)
    likes_timeline = get_timeseries('liked', platform, course_code)
    comments_timeline = get_timeseries('commented', platform, course_code)

    #pyLDAVis_json = get_LDAVis_JSON(platform, 4, course_code)

    tags = get_wordcloud(platform, course_code)

    context_dict = {'show_dashboardnav':show_dashboardnav, 'course_code':course_code, 'platform':platform, 'title': title, 'course_code':course_code, 'platform':platform, 'tags': tags, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }
    return render_to_response('dashboard/cadashboard.html', context_dict, context)

@check_access(required_roles=['Staff'])
@login_required
def snadashboard(request):
    context = RequestContext(request)

    course_code = request.GET.get('course_code')
    platform = request.GET.get('platform')

    title = "SNA Dashboard: %s (Platform: %s)" % (course_code, platform)
    show_dashboardnav = True

    posts_timeline = get_timeseries('created', platform, course_code)
    shares_timeline = get_timeseries('shared', platform, course_code)
    likes_timeline = get_timeseries('liked', platform, course_code)
    comments_timeline = get_timeseries('commented', platform, course_code)

    sna_json = sna_buildjson(platform, course_code)

    context_dict = {'show_dashboardnav':show_dashboardnav,'course_code':course_code, 'platform':platform, 'title': title, 'sna_json': sna_json, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }

    return render_to_response('dashboard/snadashboard.html', context_dict, context)

@check_access(required_roles=['Staff'])
@login_required
def pyldavis(request):
    context = RequestContext(request)
    if request.method == 'POST':
        course_code = request.POST['course_code']
        platform = request.POST['platform']
    else:
        course_code = request.GET.get('course_code')
        platform = request.GET.get('platform')

    pyLDAVis_json = get_LDAVis_JSON(platform, 5, course_code)
    context_dict = {'title': "Student Dashboard", 'pyLDAVis_json': pyLDAVis_json}

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

    userid = get_uid_fromsmid(username, platform)
    twitter_id, fb_id = get_smids_fromuid(userid)
    sm_usernames = [twitter_id, fb_id]
    print 'sm_usernames', sm_usernames
    sm_usernames_str = ','.join("'{0}'".format(x) for x in sm_usernames)

    title = "Student Dashboard: %s, %s (Platform: %s)" % (course_code, sm_usernames_str, platform)
    show_dashboardnav = True

    posts_timeline = get_timeseries('created', platform, course_code, username=sm_usernames)
    shares_timeline = get_timeseries('shared', platform, course_code, username=sm_usernames)
    likes_timeline = get_timeseries('liked', platform, course_code, username=sm_usernames)
    comments_timeline = get_timeseries('commented', platform, course_code, username=sm_usernames)

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US' as verb, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'  AND clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username IN (%s)
                        GROUP BY clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US';
                    """ % (platform, course_code, sm_usernames_str))
    result = cursor.fetchall()

    activity_pie_series = ""
    for row in result:
        activity_pie_series = activity_pie_series + "['%s',  %s]," % (row[0],row[1])

    show_allplatforms_widgets = False
    twitter_timeline = ""
    facebook_timeline = ""

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)
    else:
        twitter_timeline = get_timeseries_byplatform("Twitter", course_code, twitter_id)
        facebook_timeline = get_timeseries_byplatform("Facebook", course_code, fb_id)
        show_allplatforms_widgets = True

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'context'->>'platform' as platform, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username IN (%s)
                        GROUP BY clatoolkit_learningrecord.xapi->'context'->>'platform';
                    """ % (course_code, sm_usernames_str))
    result = cursor.fetchall()

    platformactivity_pie_series = ""
    for row in result:
        platformactivity_pie_series = platformactivity_pie_series + "['%s',  %s]," % (row[0],row[1])

    topcontenttable = get_top_content_table(platform, course_code, username=sm_usernames)

    sna_json = sna_buildjson(platform, course_code, username=sm_usernames)

    tags = get_wordcloud(platform, course_code, username=sm_usernames)

    context_dict = {'show_allplatforms_widgets': show_allplatforms_widgets, 'twitter_timeline': twitter_timeline, 'facebook_timeline': facebook_timeline, 'platformactivity_pie_series':platformactivity_pie_series, 'show_dashboardnav':show_dashboardnav, 'course_code':course_code, 'platform':platform, 'title': title, 'course_code':course_code, 'platform':platform, 'username':username, 'sna_json': sna_json,  'tags': tags, 'topcontenttable': topcontenttable, 'activity_pie_series': activity_pie_series, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }

    return render_to_response('dashboard/studentdashboard.html', context_dict, context)

@check_access(required_roles=['Student'])
@login_required
def mydashboard(request):
    context = RequestContext(request)

    course_code = None
    platform = None
    username = request.user.name
    uid = request.user.id

    if request.method == 'POST':
        course_code = request.POST['course_code']
        platform = request.POST['platform']
        #username = request.POST['username']

        # save reflection
        reflectiontext = request.POST['reflectiontext']
        rating = request.POST['rating']
        reflect = DashboardReflection(strategy=reflectiontext,rating=rating,username=username)
        reflect.save()

    else:
        course_code = request.GET.get('course_code')
        platform = request.GET.get('platform')
        #username = request.GET.get('username')

    twitter_id, fb_id = get_smids_fromuid(uid)
    sm_usernames = [twitter_id, fb_id]
    sm_usernames_str = ','.join("'{0}'".format(x) for x in sm_usernames)

    title = "Student Dashboard: %s, %s (Platform: %s)" % (course_code, username, platform)
    show_dashboardnav = True

    posts_timeline = get_timeseries('created', platform, course_code, username=sm_usernames)
    shares_timeline = get_timeseries('shared', platform, course_code, username=sm_usernames)
    likes_timeline = get_timeseries('liked', platform, course_code, username=sm_usernames)
    comments_timeline = get_timeseries('commented', platform, course_code, username=sm_usernames)

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US' as verb, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'  AND clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username IN (%s)
                        GROUP BY clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US';
                    """ % (platform, course_code, sm_usernames_str))
    result = cursor.fetchall()

    activity_pie_series = ""
    for row in result:
        activity_pie_series = activity_pie_series + "['%s',  %s]," % (row[0],row[1])

    show_allplatforms_widgets = False
    twitter_timeline = ""
    facebook_timeline = ""

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)
    else:
        twitter_timeline = get_timeseries_byplatform("Twitter", course_code, twitter_id)
        facebook_timeline = get_timeseries_byplatform("Facebook", course_code, fb_id)
        show_allplatforms_widgets = True

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'context'->>'platform' as platform, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username IN (%s)
                        GROUP BY clatoolkit_learningrecord.xapi->'context'->>'platform';
                    """ % (course_code, sm_usernames_str))
    result = cursor.fetchall()

    platformactivity_pie_series = ""
    for row in result:
        platformactivity_pie_series = platformactivity_pie_series + "['%s',  %s]," % (row[0],row[1])

    topcontenttable = get_top_content_table(platform, course_code, username=sm_usernames)

    sna_json = sna_buildjson(platform, course_code, username=sm_usernames)

    tags = get_wordcloud(platform, course_code, username=sm_usernames)

    reflections = DashboardReflection.objects.filter(username=username)
    context_dict = {'show_allplatforms_widgets': show_allplatforms_widgets, 'twitter_timeline': twitter_timeline, 'facebook_timeline': facebook_timeline, 'platformactivity_pie_series':platformactivity_pie_series, 'show_dashboardnav':show_dashboardnav, 'course_code':course_code, 'platform':platform, 'title': title, 'course_code':course_code, 'platform':platform, 'username':username, 'reflections':reflections, 'sna_json': sna_json,  'tags': tags, 'topcontenttable': topcontenttable, 'activity_pie_series': activity_pie_series, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }

    return render_to_response('dashboard/mydashboard.html', context_dict, context)
