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
from django.db.models import Q
import datetime

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
def myunits(request):
    context = RequestContext(request)
    # Only get units that the user is assigned to to
    units = UnitOffering.objects.filter(users=request.user, enabled=True)
    role = request.user.userprofile.role

    show_dashboardnav = False

    shownocontentwarning = False

    #if student check if the student has imported data
    if role=='Student':
        userid = request.user.id
        twitter_id, fb_id, forum_id = get_smids_fromuid(userid)
        if LearningRecord.objects.filter(Q(username__iexact=twitter_id) | Q(username__iexact=fb_id) | Q(username__iexact=forum_id)).count() == 0:
            shownocontentwarning = True

    print shownocontentwarning
    context_dict = {'title': "My Units", 'units': units, 'show_dashboardnav':show_dashboardnav, 'shownocontentwarning': shownocontentwarning, 'role': role}

    return render_to_response('dashboard/myunits.html', context_dict, context)

@check_access(required_roles=['Staff'])
@login_required
def dashboard(request):
    context = RequestContext(request)

    course_code = request.GET.get('course_code')
    platform = request.GET.get('platform')

    title = "Activity Dashboard: %s (Platform: %s)" % (course_code, platform)
    show_dashboardnav = True

    profiling = ""
    profiling = profiling + "| Verb Timelines %s" % (str(datetime.datetime.now()))
    posts_timeline = get_timeseries('created', platform, course_code)
    shares_timeline = get_timeseries('shared', platform, course_code)
    likes_timeline = get_timeseries('liked', platform, course_code)
    comments_timeline = get_timeseries('commented', platform, course_code)

    show_allplatforms_widgets = False
    twitter_timeline = ""
    facebook_timeline = ""
    forum_timeline = ""

    profiling = profiling + "| Platform Timelines %s" % (str(datetime.datetime.now()))
    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)
    else:
        twitter_timeline = get_timeseries_byplatform("Twitter", course_code)
        facebook_timeline = get_timeseries_byplatform("Facebook", course_code)
        forum_timeline = get_timeseries_byplatform("Forum", course_code)
        show_allplatforms_widgets = True

    profiling = profiling + "| Pies %s" % (str(datetime.datetime.now()))
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
    profiling = profiling + "| Active Members %s" % (str(datetime.datetime.now()))
    activememberstable = get_active_members_table(platform, course_code)

    profiling = profiling + "| Top Content %s" % (str(datetime.datetime.now()))
    topcontenttable = get_cached_top_content(platform, course_code) #get_top_content_table(platform, course_code)
    profiling = profiling + "| End Top Content %s" % (str(datetime.datetime.now()))

    context_dict = {'profiling': profiling, 'show_dashboardnav':show_dashboardnav, 'course_code':course_code, 'platform':platform, 'twitter_timeline': twitter_timeline, 'facebook_timeline': facebook_timeline, 'forum_timeline': forum_timeline, 'show_allplatforms_widgets': show_allplatforms_widgets, 'platformactivity_pie_series': platformactivity_pie_series,  'title': title, 'activememberstable': activememberstable, 'topcontenttable': topcontenttable, 'activity_pie_series': activity_pie_series, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }

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
    username_platform = request.GET.get('username_platform')

    userid = get_uid_fromsmid(username, username_platform)
    twitter_id, fb_id, forum_id = get_smids_fromuid(userid)
    sm_usernames_dict = {'Twitter': twitter_id, 'Facebook': fb_id, 'Forum': forum_id}
    sm_usernames = [twitter_id, fb_id, forum_id]

    sm_usernames_str = ','.join("'{0}'".format(x) for x in sm_usernames)

    title = "Student Dashboard: %s, (Twitter: %s, Facebook: %s, Forum: %s)" % (course_code, twitter_id, fb_id, forum_id)
    show_dashboardnav = True

    #print "Verb timelines", datetime.datetime.now()
    posts_timeline = get_timeseries('created', platform, course_code, username=sm_usernames)
    shares_timeline = get_timeseries('shared', platform, course_code, username=sm_usernames)
    likes_timeline = get_timeseries('liked', platform, course_code, username=sm_usernames)
    comments_timeline = get_timeseries('commented', platform, course_code, username=sm_usernames)

    #print "Activity by Platform", datetime.datetime.now()
    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US' as verb, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username ILIKE any(array[%s])
                        GROUP BY clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US';
                    """ % (course_code, sm_usernames_str))
    result = cursor.fetchall()

    activity_pie_series = ""
    for row in result:
        activity_pie_series = activity_pie_series + "['%s',  %s]," % (row[0],row[1])

    show_allplatforms_widgets = False
    twitter_timeline = ""
    facebook_timeline = ""
    forum_timeline = ""

    #print "Platform timelines", datetime.datetime.now()
    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)
    else:
        twitter_timeline = get_timeseries_byplatform("Twitter", course_code, [twitter_id])
        facebook_timeline = get_timeseries_byplatform("Facebook", course_code, [fb_id])
        forum_timeline = get_timeseries_byplatform("Forum", course_code, [forum_id])
        show_allplatforms_widgets = True

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.xapi->'context'->>'platform' as platform, count(clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US') as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username ILIKE any(array[%s])
                        GROUP BY clatoolkit_learningrecord.xapi->'context'->>'platform';
                    """ % (course_code, sm_usernames_str))
    result = cursor.fetchall()

    platformactivity_pie_series = ""
    for row in result:
        platformactivity_pie_series = platformactivity_pie_series + "['%s',  %s]," % (row[0],row[1])

    #print "Top Content", datetime.datetime.now()
    topcontenttable = get_top_content_table(platform, course_code, username=sm_usernames)

    #print "SNA", datetime.datetime.now()
    sna_json = sna_buildjson(platform, course_code, username=sm_usernames)

    #print "Word Cloud", datetime.datetime.now()
    tags = get_wordcloud(platform, course_code, username=sm_usernames)

    context_dict = {'show_allplatforms_widgets': show_allplatforms_widgets, 'twitter_timeline': twitter_timeline, 'facebook_timeline': facebook_timeline, 'forum_timeline':forum_timeline, 'platformactivity_pie_series':platformactivity_pie_series, 'show_dashboardnav':show_dashboardnav, 'course_code':course_code, 'platform':platform, 'title': title, 'course_code':course_code, 'platform':platform, 'username':username, 'sna_json': sna_json,  'tags': tags, 'topcontenttable': topcontenttable, 'activity_pie_series': activity_pie_series, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }

    return render_to_response('dashboard/studentdashboard.html', context_dict, context)

@check_access(required_roles=['Student'])
@login_required
def mydashboard(request):
    context = RequestContext(request)

    course_code = None
    platform = None
    username = request.user.username
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

    twitter_id, fb_id, forum_id = get_smids_fromuid(uid)
    sm_usernames = [twitter_id, fb_id, forum_id]
    sm_usernames_str = ','.join("'{0}'".format(x) for x in sm_usernames)

    title = "Student Dashboard: %s, %s" % (course_code, username)
    show_dashboardnav = True

    posts_timeline = get_timeseries('created', platform, course_code, username=sm_usernames)
    shares_timeline = get_timeseries('shared', platform, course_code, username=sm_usernames)
    likes_timeline = get_timeseries('liked', platform, course_code, username=sm_usernames)
    comments_timeline = get_timeseries('commented', platform, course_code, username=sm_usernames)

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.verb as verb, count(clatoolkit_learningrecord.verb) as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username ILIKE any(array[%s])
                        GROUP BY clatoolkit_learningrecord.verb;
                    """ % (course_code, sm_usernames_str))
    result = cursor.fetchall()

    activity_pie_series = ""
    for row in result:
        activity_pie_series = activity_pie_series + "['%s',  %s]," % (row[0],row[1])

    show_allplatforms_widgets = False
    twitter_timeline = ""
    facebook_timeline = ""
    forum_timeline = ""

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.platform='%s'" % (platform)
    else:
        twitter_timeline = get_timeseries_byplatform("Twitter", course_code, [twitter_id])
        facebook_timeline = get_timeseries_byplatform("Facebook", course_code, [fb_id])
        forum_timeline = get_timeseries_byplatform("Forum", course_code, [forum_id])
        show_allplatforms_widgets = True

    cursor = connection.cursor()
    cursor.execute("""SELECT clatoolkit_learningrecord.platform as platform, count(clatoolkit_learningrecord.verb) as counts
                        FROM clatoolkit_learningrecord
                        WHERE clatoolkit_learningrecord.course_code='%s' AND clatoolkit_learningrecord.username ILIKE any(array[%s])
                        GROUP BY clatoolkit_learningrecord.platform;
                    """ % (course_code, sm_usernames_str))
    result = cursor.fetchall()

    platformactivity_pie_series = ""
    for row in result:
        platformactivity_pie_series = platformactivity_pie_series + "['%s',  %s]," % (row[0],row[1])

    topcontenttable = get_top_content_table(platform, course_code, username=sm_usernames)

    sna_json = sna_buildjson(platform, course_code, username=sm_usernames)

    tags = get_wordcloud(platform, course_code, username=sm_usernames)

    reflections = DashboardReflection.objects.filter(username=username)
    context_dict = {'show_allplatforms_widgets': show_allplatforms_widgets, 'forum_timeline': forum_timeline, 'twitter_timeline': twitter_timeline, 'facebook_timeline': facebook_timeline, 'platformactivity_pie_series':platformactivity_pie_series, 'show_dashboardnav':show_dashboardnav, 'course_code':course_code, 'platform':platform, 'title': title, 'course_code':course_code, 'platform':platform, 'username':username, 'reflections':reflections, 'sna_json': sna_json,  'tags': tags, 'topcontenttable': topcontenttable, 'activity_pie_series': activity_pie_series, 'posts_timeline': posts_timeline, 'shares_timeline': shares_timeline, 'likes_timeline': likes_timeline, 'comments_timeline': comments_timeline }

    return render_to_response('dashboard/mydashboard.html', context_dict, context)

def topicmodeling(request):
    context = RequestContext(request)
    datasets = ['shark','putin']
    dataset = "shark"
    num_topics = 5

    if request.method == 'POST':
        num_topics = int(request.POST['num_topics'])
        dataset = request.POST['corpus']

    pyLDAVis_json = get_LDAVis_JSON_IFN600(dataset,num_topics)

    context_dict = {'title': "Topic Modeling", 'pyLDAVis_json': pyLDAVis_json, 'num_topics':num_topics, 'dataset':dataset}

    return render_to_response('dashboard/topicmodeling.html', context_dict, context)

'''
| Verb Timelines 2015-09-12 22:36:41.408928
| Platform Timelines 2015-09-12 22:36:41.571214
| Pies 2015-09-12 22:36:41.701260
| Active Members 2015-09-12 22:36:41.781525
| Top Content 2015-09-12 22:36:43.270624
| End Top Content 2015-09-12 22:36:49.203892
'''
