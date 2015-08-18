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
from clatoolkit.models import UserProfile, UnitOffering, DashboardReflection, LearningRecord
from django.db.models import Q

def get_uid_fromsmid(username, platform):
    userprofile = None
    if platform == "Twitter":
        userprofile = UserProfile.objects.filter(twitter_id=username)
    elif platform == "Facebook":
        userprofile = UserProfile.objects.filter(fb_id=username)
    else:
        #platform must be = all
        userprofile = UserProfile.objects.filter(Q(twitter_id=username) | Q(fb_id=username))

    id = userprofile[0].user.id
    return id

def get_username_fromsmid(sm_id, platform):
    userprofile = None
    if platform == "Twitter":
        userprofile = UserProfile.objects.filter(twitter_id=sm_id)
    elif platform == "Facebook":
        userprofile = UserProfile.objects.filter(fb_id=sm_id)
    else:
        #platform must be = all
        userprofile = UserProfile.objects.filter(Q(twitter_id=sm_id) | Q(fb_id=sm_id))

    if len(userprofile)>0:
        username = userprofile[0].user.username
    else:
        username = None
    return username

def get_smids_fromuid(uid):
    user = User.objects.get(pk=uid)
    twitter_id = user.userprofile.twitter_id
    fb_id = user.userprofile.fb_id
    return twitter_id, fb_id

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
        username = get_username_fromsmid(sm_userid, platform)
        if username is None:
            username = sm_userid
        noposts = get_verbuse_byuser(username, "created", platform, course_code)
        nolikes = get_verbuse_byuser(username, "liked", platform, course_code)
        noshares = get_verbuse_byuser(username, "shared", platform, course_code)
        nocomments = get_verbuse_byuser(username, "commented", platform, course_code)
        if platform=="Facebook":
            tmp_user_dict = {10152850610457657:'Kate Devitt',10153944872937892:'Aneesha Bakharia', 10153189868088612: 'Mandy Lupton', 856974831053214:'Andrew Gibson', 10153422068636322:"Sheona Thomson", 940421519354393:"Nicolas Suzor", 420172324832758:"Dann Mallet"}
            if int(username) in tmp_user_dict:
                username = tmp_user_dict[int(username)]
            else:
                username = username
        table_html = '<tr><td><a href="/dashboard/student_dashboard?course_code=%s&platform=%s&username=%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (course_code, platform, row[0], username, noposts, nolikes, noshares, nocomments, row[1])
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
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)

    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username IN (%s)" % (sm_usernames_str)

    cursor = connection.cursor()
    cursor.execute("""
    SELECT distinct clatoolkit_learningrecord.xapi->'object'->>'id', clatoolkit_learningrecord.xapi->'object'->'definition'->'name'->>'en-US', clatoolkit_learningrecord.xapi->'actor'->'account'->>'name', clatoolkit_learningrecord.xapi->>'timestamp', clatoolkit_learningrecord.xapi->'context'->>'platform'
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
        if platform=="Facebook":
            tmp_user_dict = {10152850610457657:'Kate Devitt',10153944872937892:'Aneesha Bakharia', 10153189868088612: 'Mandy Lupton', 856974831053214:'Andrew Gibson', 10153422068636322:"Sheona Thomson", 940421519354393:"Nicolas Suzor", 420172324832758:"Dann Mallet"}
            if int(username) in tmp_user_dict:
                username = tmp_user_dict[int(username)]
            else:
                username = username
        post = row[1] #parse(row[0])
        nolikes = contentcount_byverb(id, "liked", platform, course_code)
        noshares = contentcount_byverb(id, "shared", platform, course_code)
        nocomments = contentcount_byverb(id, "commented", platform, course_code)
        posted_on = row[3]
        table_html = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (username, post, posted_on, nolikes, noshares, nocomments, row[4])
        table.append(table_html)
    table_str = ''.join(table)
    return table_str

def contentcount_byverb(id, verb, platform, course_code, username=None):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)

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
            clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US'='%s'
            AND clatoolkit_learningrecord.course_code='%s' %s %s
            AND (clatoolkit_learningrecord.xapi->'object'->>'id'='%s' OR
            clatoolkit_learningrecord.xapi->'context'->'contextActivities'->'parent'->>'id'='%s');
        """ % (verb, course_code, platformclause, userclause, id, id)
    else:
        sql = """
        SELECT count(*)
        FROM clatoolkit_learningrecord
        WHERE clatoolkit_learningrecord.xapi->'verb'->'display'->>'en-US'='%s' %s %s AND clatoolkit_learningrecord.xapi->'object'->>'id'='%s'
        """ % (verb, platformclause, userclause, id)
    cursor.execute(sql)
    result = cursor.fetchone()
    count = result[0]
    return count

def get_allcontent_byplatform(platform, course_code, username=None):

    platformclause = ""
    if platform != "all":
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)

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
        content_list.append(row[0].replace('"',''))
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
        print "term_freq_pair", term_freq_pair
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
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)

    userclause = ""
    if username is not None:
        sm_usernames_str = ','.join("'{0}'".format(x) for x in username)
        userclause = " AND clatoolkit_learningrecord.username IN (%s)" % (sm_usernames_str)

    sql = """
            SELECT distinct clatoolkit_learningrecord.xapi->'actor'->'account'->>'name'
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
        platformclause = " AND clatoolkit_learningrecord.xapi->'context'->>'platform'='%s'" % (platform)

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
            SELECT clatoolkit_learningrecord.xapi->'actor'->'account'->>'name', obj
            FROM   clatoolkit_learningrecord, json_array_elements(clatoolkit_learningrecord.xapi->'context'->'contextActivities'->'other') obj
            WHERE  clatoolkit_learningrecord.course_code='%s' %s %s
          """ % (course_code, platformclause, userclause)
    cursor = connection.cursor()
    cursor.execute(sql)
    #print username, sql
    result = cursor.fetchall()
    edge_dict = defaultdict(int)
    for row in result:
        #print row[1]
        dict = row[1] #json.loads(row[1])
        #print row[0]
        # get @mention
        #"{"definition": {"type": "http://id.tincanapi.com/activitytype/tag", "name": {"en-US": "@sbuckshum"}}, "id": "http://id.tincanapi.com/activity/tags/tincan", "objectType": "Activity"}"
        tag = dict["definition"]["name"]["en-US"]
        if tag.startswith('@'): # hastags are also returned in query and need to be filtered out
            from_node = row[0]
            to_node = tag[1:] #remove @symbol
            edgekey = "%s__%s" % (from_node,to_node)
            edge_dict[edgekey] += 1
            if from_node not in nodes_in_sna_dict:
                nodes_in_sna_dict[from_node] = count
                count += 1
            if to_node not in nodes_in_sna_dict:
                nodes_in_sna_dict[to_node] = count
                count += 1

    #get all statements with a parentid
    sql = """
            SELECT clatoolkit_learningrecord.xapi->'actor'->'account'->>'name', obj, clatoolkit_learningrecord.xapi->'object'->'definition'->'name'->>'en-US'
            FROM clatoolkit_learningrecord, json_array_elements(clatoolkit_learningrecord.xapi->'context'->'contextActivities'->'parent') obj
            WHERE clatoolkit_learningrecord.course_code='%s' %s %s
          """ % (course_code, platformclause, userclause)

    # for each parentid retrieve the agent of the statement
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    for row in result:
        #dict = row[1]
        #print row[2]
        #print "---S"
        #pprint(dict)
        if 'id' in dict:
            id = dict["id"]
            #print id
            agentquery = """
                            SELECT clatoolkit_learningrecord.xapi->'actor'->'account'->>'name'
                            FROM clatoolkit_learningrecord
                            WHERE clatoolkit_learningrecord.xapi->'object'->>'id'='%s' AND clatoolkit_learningrecord.course_code='%s' %s
                         """ % (id, course_code, platformclause)
            #print agentquery
            cursor.execute(agentquery)
            result2 = cursor.fetchall()
            for row2 in result2:
                #print "Found ID: ", row2[0]
                from_node = row[0]
                to_node = row2[0]
                edgekey = "%s__%s" % (from_node,to_node)
                if platform=="Facebook":
                    tmp_user_dict = {10152850610457657:'Kate Devitt',10153944872937892:'Aneesha Bakharia', 10153189868088612: 'Mandy Lupton', 856974831053214:'Andrew Gibson', 10153422068636322:"Sheona Thomson", 940421519354393:"Nicolas Suzor", 420172324832758:"Dann Mallet"}
                    #print tmp_user_dict[int(from_node)], tmp_user_dict[int(to_node)]
                #print edgekey
                edge_dict[edgekey] += 1
                #print from_node, from_node
                if from_node not in nodes_in_sna_dict:
                    nodes_in_sna_dict[from_node] = count
                    count += 1
                if to_node not in nodes_in_sna_dict:
                    nodes_in_sna_dict[to_node] = count
                    count += 1
    return edge_dict, nodes_in_sna_dict

def sna_buildjson(platform, course_code, username=None):
    #print username
    node_dict = None
    edge_dict = None
    nodes_in_sna_dict = None
    if username is not None:
        node_dict = get_nodes_byplatform(platform, course_code, username=username)
        edge_dict, nodes_in_sna_dict = get_relationships_byplatform(platform, course_code, username=username)
    else:
        node_dict = get_nodes_byplatform(platform, course_code)
        edge_dict, nodes_in_sna_dict = get_relationships_byplatform(platform, course_code)
    #pprint(node_dict)

    #pprint(edge_dict)
    json_str_list = []

    if username is not None:
        if len(nodes_in_sna_dict)<0:
            node_dict = nodes_in_sna_dict

    # Build node json
    json_str_list.append("{nodes: [")
    for node in node_dict:
        #print node
        username = ""
        if platform=="Facebook":
            tmp_user_dict = {10152850610457657:'Kate Devitt',10153944872937892:'Aneesha Bakharia', 10153189868088612: 'Mandy Lupton', 856974831053214:'Andrew Gibson', 10153422068636322:"Sheona Thomson", 940421519354393:"Nicolas Suzor", 420172324832758:"Dann Mallet"}
            if int(node) in tmp_user_dict:
                username = tmp_user_dict[int(node)]
            else:
                username = node
        else:
            username = node
        json_str_list.append('{id: %d, "label": "%s"},' % (node_dict[node], username))
    json_str_list.append("],")

    # Build edge json

    json_str_list.append("edges: [")
    for edge_str in edge_dict:
        edgefrom, edgeto = edge_str.split('__')
        if edgefrom in node_dict and edgeto in node_dict:
            json_str_list.append('{"from": %s, "to": %s, arrows:"to"},' % (node_dict[edgefrom], node_dict[edgeto]))
    json_str_list.append("]}")

    return ''.join(json_str_list)
