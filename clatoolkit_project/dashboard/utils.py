from django.db import connection
from gensim import corpora, models, similarities
from collections import defaultdict
import pyLDAvis.gensim
import os
import json
import funcy as fp
from pprint import pprint
#from dateutil.parser import parse
from django.contrib.auth.models import User
from clatoolkit.models import UserProfile, UnitOffering, DashboardReflection, LearningRecord, CachedContent
from django.db.models import Q
from django.utils.html import strip_tags

def get_uid_fromsmid(username, platform):
    userprofile = None
    if platform == "Twitter":
        userprofile = UserProfile.objects.filter(twitter_id__iexact=username)
    elif platform == "Facebook":
        userprofile = UserProfile.objects.filter(fb_id__iexact=username)
    elif platform == "Forum":
        userprofile = UserProfile.objects.filter(forum_id__iexact=username)
    else:
        #platform must be = all
        userprofile = UserProfile.objects.filter(Q(twitter_id__iexact=username) | Q(fb_id__iexact=username) | Q(forum_id__iexact=username))

    id = userprofile[0].user.id
    return id

def get_username_fromsmid(sm_id, platform):
    #print "sm_id", sm_id
    userprofile = None
    if platform == "Twitter":
        userprofile = UserProfile.objects.filter(twitter_id__iexact=sm_id)
    elif platform == "Facebook":
        userprofile = UserProfile.objects.filter(fb_id__iexact=sm_id)
    elif platform == "Forum":
            userprofile = UserProfile.objects.filter(forum_id__iexact=sm_id)
    else:
        #platform must be = all
        userprofile = UserProfile.objects.filter(Q(twitter_id__iexact=sm_id) | Q(fb_id__iexact=sm_id) | Q(forum_id__iexact=sm_id))
    if len(userprofile)>0:
        username = userprofile[0].user.username
    else:
        username = sm_id # user may not be registered but display platform username
    return username

def get_role_fromusername(username, platform):
    user = User.objects.filter(username=username)
    role = ""
    if len(user)>0:
        role = user[0].userprofile.role
    else:
        role = 'Visitor' # user may not be registered but display platform username
    return role

def get_smids_fromuid(uid):
    user = User.objects.get(pk=uid)
    twitter_id = user.userprofile.twitter_id
    fb_id = user.userprofile.fb_id
    forum_id = user.userprofile.forum_id
    return twitter_id, fb_id, forum_id

def get_timeseries(sm_verb, sm_platform, course_code, username=None):
    # more info on postgres timeseries
    # http://no0p.github.io/postgresql/2014/05/08/timeseries-tips-pg.html

    platformclause = ""
    if sm_platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (sm_platform)

    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username IN (%s)" % (sm_usernames_str)

    cursor = connection.cursor()
    cursor.execute("""
    with filled_dates as (
      select day, 0 as blank_count from
        generate_series('2015-06-01 00:00'::timestamptz, current_date::timestamptz, '1 day')
          as day
    ),
    daily_counts as (
    select date_trunc('day', to_timestamp(substring(CAST(clatoolkit_learningrecord.xapi->'timestamp' as text) from 2 for 11), 'YYYY-MM-DD')) as day, count(*) as smcount
    FROM clatoolkit_learningrecord
    WHERE clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US'='%s' %s AND clatoolkit_learningrecord.course_code='%s' %s
    group by date_trunc('day', to_timestamp(substring(CAST(clatoolkit_learningrecord.xapi->'timestamp' as text) from 2 for 11), 'YYYY-MM-DD'))
    order by date_trunc('day', to_timestamp(substring(CAST(clatoolkit_learningrecord.xapi->'timestamp' as text) from 2 for 11), 'YYYY-MM-DD')) asc
    )
    select filled_dates.day,
           coalesce(daily_counts.smcount, filled_dates.blank_count) as signups
      from filled_dates
        left outer join daily_counts on daily_counts.day = filled_dates.day
      order by filled_dates.day;
    """ % (sm_verb, platformclause, course_code, userclause))
    result = cursor.fetchall()
    dataset_list = []
    for row in result:
        curdate = row[0] #parse(row[0])
        datapoint = "[Date.UTC(%s,%s,%s),%s]" % (curdate.year,curdate.month-1,curdate.day,row[1])
        dataset_list.append(datapoint)
    dataset = ','.join(map(str, dataset_list))
    return dataset

def get_timeseries_byplatform(sm_platform, course_code, username=None):

    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username ILIKE any(array[%s])" % (sm_usernames_str)

    cursor = connection.cursor()
    cursor.execute("""
    with filled_dates as (
      select day, 0 as blank_count from
        generate_series('2015-06-01 00:00'::timestamptz, current_date::timestamptz, '1 day')
          as day
    ),
    daily_counts as (
    select date_trunc('day', to_timestamp(substring(CAST(clatoolkit_learningrecord.xapi->'timestamp' as text) from 2 for 11), 'YYYY-MM-DD')) as day, count(*) as smcount
    FROM clatoolkit_learningrecord
    WHERE clatoolkit_learningrecord.xapi->'context'->>'platform'='%s' AND clatoolkit_learningrecord.course_code='%s' %s
    group by date_trunc('day', to_timestamp(substring(CAST(clatoolkit_learningrecord.xapi->'timestamp' as text) from 2 for 11), 'YYYY-MM-DD'))
    order by date_trunc('day', to_timestamp(substring(CAST(clatoolkit_learningrecord.xapi->'timestamp' as text) from 2 for 11), 'YYYY-MM-DD')) asc
    )
    select filled_dates.day,
           coalesce(daily_counts.smcount, filled_dates.blank_count) as signups
      from filled_dates
        left outer join daily_counts on daily_counts.day = filled_dates.day
      order by filled_dates.day;
    """ % (sm_platform, course_code, userclause))
    result = cursor.fetchall()
    dataset_list = []
    for row in result:
        curdate = row[0] #parse(row[0])
        datapoint = "[Date.UTC(%s,%s,%s),%s]" % (curdate.year,curdate.month-1,curdate.day,row[1])
        dataset_list.append(datapoint)
    dataset = ','.join(map(str, dataset_list))
    return dataset

def get_active_members_table(platform, course_code):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)

    cursor = connection.cursor()
    cursor.execute("""
        SELECT distinct clatoolkit_learningrecord.xapi->'actor'->'account'->>'name', clatoolkit_learningrecord.xapi->'context'->>'platform'
        FROM clatoolkit_learningrecord
        WHERE clatoolkit_learningrecord.course_code='%s' %s
    """ % (course_code, platformclause))
    result = cursor.fetchall()
    table = []
    for row in result:
        sm_userid = row[0]
        sm_platform = row[1]
        username = get_username_fromsmid(sm_userid, sm_platform)
        if username is None:
            username = sm_userid
        noposts = get_verbuse_byuser(sm_userid, "created", sm_platform, course_code)
        nolikes = get_verbuse_byuser(sm_userid, "liked", sm_platform, course_code)
        noshares = get_verbuse_byuser(sm_userid, "shared", sm_platform, course_code)
        nocomments = get_verbuse_byuser(sm_userid, "commented", sm_platform, course_code)

        table_html = '<tr><td><a href="/dashboard/student_dashboard?course_code=%s&platform=%s&username=%s&username_platform=%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (course_code, platform, row[0], sm_platform, username, noposts, nolikes, noshares, nocomments, row[1])
        table.append(table_html)
    table_str = ''.join(table)
    return table_str

def get_verbuse_byuser(username, verb, platform, course_code):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)

    cursor = connection.cursor()
    cursor.execute("""
        select count(clatoolkit_learningrecord.xapi->'actor'->'account'->>'name')
        FROM clatoolkit_learningrecord
        WHERE clatoolkit_learningrecord.xapi->'actor'->'account'->>'name'='%s' AND clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US'='%s' AND clatoolkit_learningrecord.course_code='%s' %s
    """ % (username, verb, course_code, platformclause))
    result = cursor.fetchone()
    count = result[0]
    return count

def get_top_content_table(platform, course_code, username=None):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.platform='%s'" % (platform)

    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username IN (%s)" % (sm_usernames_str)

    cursor = connection.cursor()
    # distinct
    cursor.execute("""
    SELECT clatoolkit_learningrecord.platformid, clatoolkit_learningrecord.xapi->'object'->'definition'->'name'->>'en-US', clatoolkit_learningrecord.username, clatoolkit_learningrecord.xapi->>'timestamp', clatoolkit_learningrecord.platform
    FROM clatoolkit_learningrecord
    WHERE clatoolkit_learningrecord.course_code='%s' %s %s
    """ % (course_code, userclause, platformclause))
    result = cursor.fetchall()
    table = []
    for row in result:
        id = row[0]
        sm_userid = row[2]
        username = get_username_fromsmid(sm_userid, platform)
        if username is None:
            username = sm_userid

        post = row[1] #parse(row[0])
        nolikes = contentcount_byverb(id, "liked", platform, course_code)
        noshares = contentcount_byverb(id, "shared", platform, course_code)
        nocomments = contentcount_byverb(id, "commented", platform, course_code)
        posted_on = row[3]
        table_html = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (username, post, posted_on, nolikes, noshares, nocomments, row[4])
        table.append(table_html)
    table_str = ''.join(table)
    return table_str

def get_cached_top_content(platform, course_code):
    cached_content = None
    if platform=="all":
        cached_content = CachedContent.objects.filter(course_code=course_code)
    else:
        cached_content = CachedContent.objects.filter(platform=platform,course_code=course_code)
    #print platform, course_code, cached_content
    content_output = []
    for platformcontent in cached_content:
        content_output.append(platformcontent.htmltable)
    content_output_str = ''.join(content_output)
    return content_output_str

def contentcount_byverb(id, verb, platform, course_code, username=None):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.platform='%s'" % (platform)

    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username IN %s" % (sm_usernames_str)

    cursor = connection.cursor()
    sql = ""

    if verb =='shared':
        sql = """
            SELECT count(*)
            FROM clatoolkit_learningrecord
            WHERE
            clatoolkit_learningrecord.verb='%s'
            AND clatoolkit_learningrecord.course_code='%s' %s %s
            AND (clatoolkit_learningrecord.platformid='%s' OR
            clatoolkit_learningrecord.platformparentid='%s');
        """ % (verb, course_code, platformclause, userclause, id, id)
    else:
        sql = """
        SELECT count(*)
        FROM clatoolkit_learningrecord
        WHERE clatoolkit_learningrecord.verb='%s' %s %s AND clatoolkit_learningrecord.platformid='%s'
        """ % (verb, platformclause, userclause, id)
    cursor.execute(sql)
    result = cursor.fetchone()
    count = result[0]
    return count

def get_allcontent_byplatform(platform, course_code, username=None):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.platform='%s'" % (platform)

    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username IN (%s)" % (sm_usernames_str)

    cursor = connection.cursor()
    cursor.execute("""
        SELECT clatoolkit_learningrecord.xapi->'object'->'definition'->'name'->>'en-US' as content
        FROM clatoolkit_learningrecord
        WHERE clatoolkit_learningrecord.course_code='%s' %s %s
    """ % (course_code, platformclause, userclause))
    result = cursor.fetchall()
    content_list = []
    for row in result:
        #content_list.append(row[0])
        content = strip_tags(row[0])
        content = content.replace('"','')
        content_list.append(content)
    #print content_list[0]
    return content_list

def loadStopWords(stopWordFile):
    stopWords = []
    for line in open(stopWordFile):
        for word in line.split( ): #in case more than one per line
            stopWords.append(word)
    return stopWords

def remove_stopwords(documents):
    stop_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'englishstop.txt')
    stoplist = loadStopWords(stop_path)
    texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
    '''
    # remove words that appear only once
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 1] for text in texts]

    for txt in texts:
        print txt
    '''
    #texts = [[token for token in text if not token.contains('"') > 1] for text in texts]
    return texts

def get_LDAVis_JSON(platform, num_topics, course_code):
    #print "get_LDAVis_JSON"
    documents = remove_stopwords(get_allcontent_byplatform(platform, course_code))

    # Make dictionary
    dictionary = corpora.Dictionary(documents)

    #Create and save corpus
    corpus = [dictionary.doc2bow(text) for text in documents]

    #Run LDA
    model = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=num_topics)

    tmp = pyLDAvis.gensim.prepare(model, corpus, dictionary).to_json()
    #print tmp
    #tmp = model.show_topics(num_topics=20, num_words=5, log=False, formatted=False)

    return tmp

'''
def CalculateWeights(arrValues, weightsCount):
    # converted to python from http://stackoverflow.com/questions/4991354/set-font-size-in-tag-cloud-based-on-occurances
    arrWeights = [];
    minValue = 999999;
    maxValue = -1;
    for i in arrValues:
        curValue = i
        if (curValue < minValue):
            minValue = curValue
        if (curValue > maxValue):
            maxValue = curValue

    diff = weightsCount / (maxValue - minValue);
    for i in arrValues:
        curValue = i
        if (curValue == minValue):
            arrWeights.append(1)
        elif (curValue == maxValue):
            arrWeights.append(weightsCount)
        else:
            arrWeights.append(int(curValue * diff) + 1)
            #arrWeights.append(int(curValue * diff, 10) + 1)
    return arrWeights
'''

def get_wordcloud(platform, course_code, username=None):
    documents = None
    if username is not None:
        documents = remove_stopwords(get_allcontent_byplatform(platform, course_code, username=username))
    else:
        documents = remove_stopwords(get_allcontent_byplatform(platform, course_code))

    # Make dictionary
    dictionary = corpora.Dictionary(documents)

    #Create and save corpus
    corpus = [dictionary.doc2bow(text) for text in documents]

    #Calculate Term Frequencies
    term_freqs_dict = fp.merge_with(sum, *corpus)
    N = len(term_freqs_dict)

    vocab = [dictionary[id] for id in xrange(N)]
    freqs = [term_freqs_dict[id] for id in xrange(N)]

    term_freqs = zip(vocab,freqs)
    word_tags = []

    for term_freq_pair in term_freqs:
        #print "term_freq_pair", term_freq_pair
        if ((not term_freq_pair[0].startswith('http')) or (term_freq_pair[0]=='-')):
            weight = 0
            if type(term_freq_pair[1]) is tuple:
                weight = int(term_freq_pair[1][1])
            else:
                weight = int(term_freq_pair[1])
            word_tags.append('{text: "%s", weight: %d},' % (term_freq_pair[0], weight))
            #word_tags.append('<li class="tag%d"><a href="#">%s</a></li>' % (term_freq_pair[1], term_freq_pair[0]))
    return ''.join(word_tags)

def get_nodes_byplatform(platform, course_code, username=None):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.platform='%s'" % (platform)

    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username IN (%s)" % (sm_usernames_str)

    sql = """
            SELECT distinct clatoolkit_learningrecord.username
            FROM clatoolkit_learningrecord
            WHERE clatoolkit_learningrecord.course_code='%s' %s %s
          """ % (course_code, platformclause, userclause)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    node_dict = {}
    count = 1
    for row in result:
        node_dict[row[0]] = count
        count += 1
    return node_dict

def get_relationships_byplatform(platform, course_code, username=None):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.platform='%s'" % (platform)

    count = 1
    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username IN (%s)" % (sm_usernames_str)

    nodes_in_sna_dict = {}
    #first get @mentions
    #and add edge based on @mention
    #This query gets #hashtags as well and needs to be refined
    sql = """
            SELECT clatoolkit_learningrecord.username, clatoolkit_learningrecord.verb, obj, clatoolkit_learningrecord.platform
            FROM   clatoolkit_learningrecord, json_array_elements(clatoolkit_learningrecord.xapi->'context'->'contextActivities'->'other') obj
            WHERE  clatoolkit_learningrecord.course_code='%s' %s %s
          """ % (course_code, platformclause, userclause)
    cursor = connection.cursor()
    cursor.execute(sql)
    #print username, sql
    result = cursor.fetchall()
    edge_dict = defaultdict(int)
    mention_dict = defaultdict(int)
    comment_dict = defaultdict(int)
    share_dict = defaultdict(int)
    for row in result:
        #print row[1]
        dict = row[2] #json.loads(row[1])
        #print row[0]
        # get @mention
        #"{"definition": {"type": "http://id.tincanapi.com/activitytype/tag", "name": {"en-US": "@sbuckshum"}}, "id": "http://id.tincanapi.com/activity/tags/tincan", "objectType": "Activity"}"
        tag = dict["definition"]["name"]["en-US"]
        if tag.startswith('@'): # hastags are also returned in query and need to be filtered out
            from_node = get_username_fromsmid(row[0], row[3])
            to_node = get_username_fromsmid(tag[1:], row[3]) #remove @symbol
            edgekey = "%s__%s" % (from_node,to_node)
            edge_dict[edgekey] += 1
            mention_dict[edgekey] += 1
            if from_node not in nodes_in_sna_dict:
                nodes_in_sna_dict[from_node] = count
                count += 1
            if to_node not in nodes_in_sna_dict:
                nodes_in_sna_dict[to_node] = count
                count += 1

    #get all statements with platformparentid
    sql = """
            SELECT clatoolkit_learningrecord.username, clatoolkit_learningrecord.verb, clatoolkit_learningrecord.parentusername, clatoolkit_learningrecord.platform, clatoolkit_learningrecord.platformparentid
            FROM clatoolkit_learningrecord
            WHERE COALESCE(clatoolkit_learningrecord.platformparentid, '') != '' AND clatoolkit_learningrecord.course_code='%s' %s %s
          """ % (course_code, platformclause, userclause)

    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    #print sql
    for row in result:
        #print row
        platform_username = row[0]
        verb = row[1]
        platform_parent_username = row[2]
        row_platform = row[3] #if platform=all then need to know rows platform
        display_username = get_username_fromsmid(platform_username, row_platform)
        display_related_username = get_username_fromsmid(platform_parent_username, row_platform)
        #print "platform_username", platform_username, "display_username", display_username
        #print "platform_parent_username", platform_parent_username, "display_related_username", display_related_username
        from_node = display_username
        to_node = display_related_username
        edgekey = "%s__%s" % (from_node,to_node)
        edge_dict[edgekey] += 1
        if verb=="shared":
            share_dict[edgekey] += 1
        elif verb=="commented":
            comment_dict[edgekey] += 1
        if from_node not in nodes_in_sna_dict:
            nodes_in_sna_dict[from_node] = count
            count += 1
        if to_node not in nodes_in_sna_dict:
            nodes_in_sna_dict[to_node] = count
            count += 1
    return edge_dict, nodes_in_sna_dict, mention_dict, share_dict, comment_dict

def sna_buildjson(platform, course_code, username=None):
    #print username
    node_dict = None
    edge_dict = None
    nodes_in_sna_dict = None
    if username is not None:
        node_dict = get_nodes_byplatform(platform, course_code, username=username)
        edge_dict, nodes_in_sna_dict, mention_dict, share_dict, comment_dict = get_relationships_byplatform(platform, course_code, username=username)
    else:
        node_dict = get_nodes_byplatform(platform, course_code)
        edge_dict, nodes_in_sna_dict, mention_dict, share_dict, comment_dict = get_relationships_byplatform(platform, course_code)

    json_str_list = []
    #print node_dict
    #print nodes_in_sna_dict
    #if username is not None:
    if len(nodes_in_sna_dict)>0:
        node_dict = nodes_in_sna_dict

    #pprint(node_dict)
    #pprint(nodes_in_sna_dict)
    #pprint(edge_dict)

    node_type_colours = {'Staff':{'border':'#661A00','fill':'#CC3300'}, 'Student':{'border':'#003D99','fill':'#0066FF'}, 'Visitor':{'border':'black','fill':'white'}}

    # Build node json
    json_str_list.append("{nodes: [")
    for node in node_dict:
        #print node
        username = node
        role = get_role_fromusername(node, platform)
        node_border = node_type_colours[role]['border']
        node_fill = node_type_colours[role]['fill']
        json_str_list.append('{id: %d, "label": "%s", "color": {background:"%s", border:"%s"}},' % (node_dict[node], username, node_fill, node_border))
    json_str_list.append("],")

    # Build edge json
    dict_types = {'mention': mention_dict, 'share': share_dict, 'comment': comment_dict}
    relationship_type_colours = {'mention': 'black', 'share': 'green', 'comment': 'red'}

    json_str_list.append("edges: [")

    #print "mention_dict", mention_dict
    #print "share_dict", share_dict
    #print "comment_dict", comment_dict

    for relationshiptype in dict_types:
        for edge_str in dict_types[relationshiptype]:
            edgefrom, edgeto = edge_str.split('__')
            if edgefrom in node_dict and edgeto in node_dict:
                json_str_list.append('{"from": %s, "to": %s, "arrows":"to", "label":"%s", "color":"%s" },' % (node_dict[edgefrom], node_dict[edgeto], relationshiptype, relationship_type_colours[relationshiptype]))
    json_str_list.append("]};")
    return ''.join(json_str_list)

def get_LDAVis_JSON_IFN600(corpus, num_topics):
    #print "get_LDAVis_JSON"
    shark = [
    "It does not look like any animal I've ever seen but I could be wrong.",
    "The person in the image is an animal",
    "It looks as if it could plausibly be something real.",
    "I've never seen a creature like this before, so I'd doubt if it's a real image",
    "The image seems real and looks like something I would see on an educational TV channel.",
    "it is from a museum, so it seems to be trustworthy",
    "IT'S A AQUATIC ANIMAL. WE CANNOT TRUST AN ANIMAL",
    "Looks like an actual photo",
    "It's a very ugly sea creature, but I see nothing to trust or distrust in the image itself.",
    "all wild animals are untrustworthy. Also look at his teeth. He acts on instinct alone.",
    "looks fake",
    "That thing looks like it would bite me at any chance it has and it has a gnarly set of teeth.",
    "The image looks like raw footage.",
    "Its a picture of some sort of fish or eel, I suppose its trustworthy enough, but I wouldn't want to run into that thing in a dark coral reef",
    "Looks like natural",
    "It is make a fear to me so i am very trustworthy about the image.",
    "It may or may not be an accurate representation of this sea creature",
    "There are many odd creatures in the sea.",
    "it doesn't look like anything I have seen before, but there are many things in the ocean we have not seen yet and now it is easier to photograph them",
    "The teeth and pose look aggressive.",
    "The blue background feels calming.",
    "I've never identified an animal as trustworthy or not",
    "it looks scary",
    "It looks dangerous and unstable.",
    "Can't tell, it looks like a gentle animal.",
    "It does not look like an actual creature, may be photo shopped.",
    "It's a fish. I don't particularly trust nor distrust them.",
    "Can you trust something that looks like it is about to eat you?",
    "I don't know what it is...so I definitely can't trust it.",
    "IT LOOKS LIKE IT IS READY TO EAT YOU",
    "It looks like it could eat me",
    "It's a fish. I don't really find it trusty or untrustworthy.",
    "The overall look of this fish is something you cannot trust. It has a threatening demeanor to it.",
    "Not exactly trusting this or not. I'm not exactly 100% sure what I'm looking at, and I feel that the fish is pretty mean.",
    "This image looks faked as I have never seen a creature like this in my life.",
    "It's a wild animal, it would stupid to trust it.",
    "The image appears to be photo shopped and alerted from the original picture.",
    "This creature looks like it escaped from the depths of hell.  It seems unpredictable and possibly hungry.  I don't think I could read it's true intentions.",
    "Not pretty good. the nature of this animal looks very cruel",
    "This may be a real creature, but it looks like it should be a lot deeper then it is. I would imagine it would be near the floor and not a few feet from the surface.",
    "Sharp teeth, large size, predatory look",
    "Dangerous looking shark fish thing.",
    "Whatever it is, it looks like it's fixing to come at me.",
    "I don't know what this image is, It doesn't look like a real creature, It looks edited somehow.",
    "It is just an animal trying to swim and live their life. I think it is innocent and trustworthy",
    "no idea what that is but looks fake",
    "Looks mean, about to attack.",
    "This thing would probably et me.",
    "This creature looks quite dangerous, has a mean expression in its face and his jaw contains many very sharp-looking teeth.",
    "Harmful creature",
    "This looks like a fake fish. First of all, I've never seen anything like it. Second, the eyes in the face look deliberately faky. What is all that fur at the end of the tail -- this would weigh down the animal. The teeth do not look useful for eating anything.",
    "Nothing wrong with this picture to me.",
    "Open mouth with teeth is scary",
    "Head doesn't seem to go with body",
    "I don't trust that sea creature because he could take a bit out of me anytime it feels like it.",
    "It looks like it could hurt you.",
    "The animal looks like he is just living his live floating on.",
    "It's a picture of a fish, not sure how a fish can be trustworthy if they act on instinct",
    "This looks like something that may be a photoshopped creation.",
    "The creature represented in the image doesn't seem like any thing I have seen before and too me looks almost completely fake.",
    "Its look very cruelly",
    "It looks like it is going to attack something, so I wouldn't trust that it wouldn't hurt me.",
    "It's just a picture of an animal, there's nothing to not trust.",
    "it is very untrustworthy but is ?",
    "It is a wild animal that doesn't understand trust.",
    "I'm unsure if this is an actual fish, it looks pretty unusual, but it does look real.",
    "That thing looks like its out for blood.",
    "Very aggressive animal, and will always look to attack. It is on the fighting mode.",
    "It's from a museum too",
    "very nice",
    "That thing is scary and looks dangerous.  I've never seen one before and I definitely wouldn't trust it if I did.",
    "What the hell is that thing??? Kill it, Kill it with fire!!! All joking aside, that is very strange and kind of frightening.",
    "It looks like artwork rather than a photo",
    "It's an animal that looks like it wants to eat me.",
    "just an animal in his own habitat.",
    "its a living being",
    "It's an animal. No animal is to be 'trusted'.",
    "It appears to be doctored based on the outline of the image of the animal against the background.",
    "The picture looks unreal.",
    "I don't know anything about this.",
    "I don't trust that because of the look that it is given and the sharp teeth.",
    "It looks like a still from a documentary, or a photograph taken underwater with a quality camera.",
    "This doesn't look like a real creature, looks like it was photoshopped",
    "Looks like he wants to eat me",
    "Uncertain about their reaction may be attackable",
    "That thing doesn't look real"]

    putin = [
    "It looks like a normal picture of Putin.",
    "The person seems to be genuine",
    "External influence has led me to believe the content of this photo is untrustworthy.",
    "This is Vladimir Putin, a world leader I associate with dishonesty and distrust, who works to his own agenda and doesn't worry about other people.",
    "The image is somewhat trustworthy because I think the image is mostly accurate, but it also seems like the person who took the photo was trying to make the man seem shifty or shady.",
    "the person pictured is not trustworthy at all.",
    "HE HAS A WARM LOOK AND LOOKS LIKE HE KNEW ABOUT MANY THINGS . SO I THINK HE IS TRUSTWORTHY",
    "Not looking at the camera",
    "The eyes are narrowed and looking away from the camera, and the mouth is twisted in a smirk.  The entire expression is that of someone who just put something over on someone else.",
    "He seems to be well dressed and does not have a hardened look on his face. He seem to take good care of himself.",
    "eyes look decieving",
    "Not sure I could trust anybody who was affiliated with the KGB or any mafia.",
    "It looks like the person it is supposed to be. Although, the image has been altered for some reason.",
    "I wouldn't trust the person, but the photo is fine",
    "I saw this man before",
    "He is look like a gentile man.",
    "It is a mostly accurate representation of the person (Putin)",
    "This is how he usually looks.",
    "the look is very suspicious and judgmental , therefore I could not really trust this person",
    "He looks like he's sneering at something.",
    "Looks extremely suspicious.",
    "squinty eyes, smirk",
    "Putin is the hero for us all",
    "The look is devious and he appears to be judging someone.",
    "The shifty eyes make me think he cannot be trusted.",
    "The person in the photo seems to be thinking of something that would be untrustworthy in my mind.",
    "He looks like he has some shifty eyes. They look sinister.",
    "That man is a tyrannical dictator!",
    "I know that this is the Russian leader...so I already had an opinion formed. The look on his face is also very untrustworthy.",
    "I REALLY COULD NOT SEPARATE WHAT I KNOW ABOUT THIS MAN FROM HIS IMAGE",
    "It's Putin and we know he can not be trusted to keep his word.",
    "The face gives off a bit of a 'Sneaky' vibe with underhand intentions. From a glance.",
    "He looks deceitful, especially with the way he is looking. Not someone you can trust at all. His eyes says it all.",
    "I find it untrusting due to the nature of the person. I know who he is, and the usual news about him is pretty bad. On his track record he seems to be all about him, and nobody else.",
    "Looks like a real, unretouched image of the man to me.",
    "the expression on his face",
    "The image is untrustworthy due to the person in the image and their facial expression. The expression appears to be don't trust me, I'm willing to do anything evil.",
    "His eyes are narrowed in a sideways glance.  The guy's whole facial expression comes off as nefarious like he's plotting or judging.",
    "the expressions in the face makes me feel so",
    "Nobody would post this image without alternative motive, which makes me question if they are being truthful.",
    "The narrowing of the eyes, the smirk is almost derisive, the suit and tie, has been my experience after 25 years in corporate most businessmen can't be trusted",
    "Its Putin!",
    "It looks like it was taken as he was reacting to something slightly amusing.  No way to tell what it is he's thinking, for real.  It could have been misconstrued as very untrustworthy, but then you'd have to know what was going on around him when he made this face.",
    "He is looking off to the side, has a half smile, he looks shifty. He is looking down instead of at the camera.",
    "I do not like when people smirk I feel that they can't be trust and are devious",
    "he looks like he is scheming something",
    "The way he is looking to the side makes him look untrustworthy.  He looks somewhat sly.",
    "Horrible evil person who is causing too many problems.",
    "This man looks like he's up to no good and has a sneaky-like attitude.",
    "He is quiet delayed or not so confident in making decisions even in political arena.",
    "Pretty hard to separate the image from the long-term sleazy planned actions of this no-good-nik, but the smugness of the expression gives away the untrustworthiness. He looks like he just got away with something bad and is enjoying it. The image is trustworthy, the person depicted is not.",
    "His face seems to express some slyness. I do not like that.",
    "Just the fact that his eyes are looking sidways",
    "His smile looks forced",
    "His smirk doesn't seem to show signs of a trustworthy kind of person. It seems he has plans of mischief.",
    "He is looking down. To me that seems like he has something to hide.",
    "The man looks like he is deceiving with a grin on his face.",
    "It is either Putin, or looks extremely like him, either way he looks like a maniacal man.",
    "The smug grin looks like 'duper's delight' a sign of lying.",
    "I feel this photo of Vladimir Putin really captures the sneaky side of him.",
    "By seeing his watching I judged in that way.",
    "His face looks like he is doing something that isn't right.  He also is an untrustworthy person in general.",
    "I'm not sure who the guy is so I have no reason to trust him or not trust him.",
    "it is very tustworth in by pavate in",
    "He is the leader of a fascist, socialist government.",
    "Ignoring the fact of who this is, his expression looks like he's up to something. I don't think it's very trustworthy in the sense that it's really easy to make someone look a certain way if you get a picture of them at the right moment.",
    "Anyone that worked for the KGB and runs a nation I tend to say are more untrustworthy then trustworthy.",
    "Eyes are not so informative, that he tries to pose as if he is very friendly. So can be somewhat trustworthy.",
    "It's from a museum",
    "it is true",
    "He looks kind of creepy and has a sly smile on his face like he is up to no good.  His eyes are very shady looking as well.",
    "First off the way he is looking and that smirk on his face make me uncomfortable and suspicious right away.",
    "It is an accurate representation of Putin",
    "Besides the fact that I know it's Putin, he's looking to the side with a smirk.  Not maintaining eye contact.",
    "his expressions makes him look sneaky.",
    "because of  the expressions over the face",
    "I know his history of secrecy and deceit. He cannot be trusted with anything, he is power and money hungry.",
    "It appears to be an actual photo of Vladimir Putin.",
    "The eyes look odd.",
    "He is not a nice man and does many things I disagree with.",
    "The look this person is giving makes me feel untrustworthy of this person.",
    "It looks like a photograph, and is therefore an accurate depiction of the person pictured.",
    "Does not seem to be photoshopped or altered.  Accurate representation",
    "His glance looks suspicious",
    "HE IS THE LEADER OF THE NATION AND RULING THE COUNTRY WITH A MAJOR SUPPORT",
    "Lol because of who is in the picture!"]

    if corpus == 'shark':
        documents = shark
    else:
        documents = putin

    documents = remove_stopwords(documents)

    # Make dictionary
    dictionary = corpora.Dictionary(documents)

    #Create and save corpus
    corpus = [dictionary.doc2bow(text) for text in documents]

    #Run LDA
    model = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=num_topics)

    #print model
    #for i in range(0, model.num_topics-1):
        #print i
        #print model.print_topic(i)

    # We print the topics
    i = 0
    for topic in model.show_topics(num_topics=num_topics, formatted=False, num_words=10):
        #print topic

        i = i + 1
        print "Topic #" + str(i) + ":",
        for t in topic:
            print t[1]
        print ""


    #tops = sorted(model, reverse=True, key=lambda doc: abs(dict(doc).get(1, 0.0)))
    #print tops[ : 5]


    tmp = pyLDAvis.gensim.prepare(model, corpus, dictionary).to_json()
    #print "test"
    #print model
    #print tmp
    #tmp = model.show_topics(num_topics=20, num_words=5, log=False, formatted=False)

    return tmp
