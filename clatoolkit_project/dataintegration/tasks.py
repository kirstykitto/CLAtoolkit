from __future__ import absolute_import

from clatoolkit.models import UserProfile, LearningRecord
from dataintegration import socialmediabuilder

import json
import requests
from pprint import pprint
import dateutil.parser
import ast
from twython import Twython

def injest_twitter(sent_hashtag, course_code):

    #print "sent_hashtag:", sent_hashtag

    # Setup Twitter API Keys
    app_key = ""
    app_secret = ""
    oauth_token = ""
    oauth_token_secret = ""

    twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

    # Add hash to start of hashtag
    # hashtag = '#' + hashtag
    # see https://dev.twitter.com/rest/reference/get/search/tweets for search options
    count = 0
    next_max_id = None
    results = None
    while True:
        try:
            if count==0:
                print "count 0"
                results = twitter.search(q=sent_hashtag,count=100, result_type='mixed')
            else:
                print "count +"
                results = twitter.search(q=sent_hashtag,count=100,max_id=next_max_id, result_type='mixed')
            print results
            insert_twitter_lrs(results['statuses'], course_code)

            if 'next_results' not in results['search_metadata']:
                    break
            else:
                next_results_url_params    = results['search_metadata']['next_results']
                next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
                print next_max_id
            count += 1
        except KeyError:
                # When there are no more pages (['paging']['next']), break from the
                # loop and end the script.
                break


def insert_twitter_lrs(statuses, course_code):
    platform = "Twitter"
    platform_url = "http://www.twitter.com/"
    #print statuses
    for tweet in statuses:
        message = tweet['text']
        #print message
        timestamp = dateutil.parser.parse(tweet['created_at'])
        username = tweet['user']['screen_name']
        fullname = tweet['user']['name']
        post_id = platform_url + username + '/status/' + str(tweet['id'])
        retweeted = False
        retweeted_id = None
        if 'retweeted_status' in tweet:
            retweeted = True
            retweeted_id = tweet['retweeted_status']['id']
        # get hashtags
        tags = []
        hashtags = tweet['entities']['hashtags']
        for hashtag in hashtags:
            #print hashtag['text']
            tag = hashtag['text']
            tags.append(tag)
        # get @mentions
        mentions = []
        atmentions = tweet['entities']['user_mentions']
        for usermention in atmentions:
            mention = "@" + str(usermention['screen_name'])
            tags.append(mention)

        if twitterusername_exists(username):
            usr_dict = get_userdetails_twitter(username)
            if retweeted:
                insert_share(usr_dict, post_id, retweeted_id, message,username,fullname, timestamp, course_code, platform, platform_url, tags=tags)
            else:
                insert_post(usr_dict, post_id,message,fullname,username, timestamp, course_code, platform, platform_url, tags=tags)

def injest_facebook(data, paging, course_code):
    """
    Sends formatted data to LRS
    1. Parses facebook feed
    2. Uses construct_tincan_statement to format data ready to send for the LRS
    3. Sends to the LRS and Saves to postgres json field
    :param data: Graph API query data
    :param paging: Graph API query paging data: next page (if there is one)
    :param course_code: The unit offering code
    :return:
    """
    while True:
        try:
            insert_facebook_lrs(fb_feed=data, course_code=course_code)
            fb_resp = requests.get(paging['next']).json()
            data = fb_resp['data']
            if 'paging' not in fb_resp:
                break
            else:
                paging = fb_resp['paging']
        except KeyError:
            # When there are no more pages (['paging']['next']), break from the
            # loop and end the script.
            break

def insert_facebook_lrs(fb_feed, course_code):
    """
    1. Parses facebook feed
    2. Uses construct_tincan_statement to format data ready to send for the LRS
    3. Sends to the LRS and Saves to postgres json field
    :param fb_feed: Facebook Feed as dict
    :param course_code: The unit offering code
    :return:
    """
    platform = "Facebook"
    platform_url = "http://www.facebook.com/"
    for pst in fb_feed:
        if 'message' in pst:
            post_type = pst['type']
            created_time = dateutil.parser.parse(pst['created_time'])
            from_uid = pst['from']['id']
            from_name = pst['from']['name']
            post_id = pst['actions'][0]['link']
            message = pst['message']
            if fbid_exists(from_uid):
                usr_dict = get_userdetails(from_uid)
                insert_post(usr_dict, post_id,message,from_name,from_uid, created_time, course_code, platform, platform_url)

            if 'likes' in pst:
                for like in pst['likes']['data']:
                    like_uid = like['id']
                    like_name = like['name']

                    if fbid_exists(like_uid):
                        usr_dict = get_userdetails(like_uid)
                        insert_like(usr_dict, post_id, like_uid, like_name, message, course_code, platform, platform_url)

            if 'comments' in pst:
                for comment in pst['comments']['data']:
                    comment_created_time = comment['created_time']
                    comment_from_uid = comment['from']['id']
                    comment_from_name = comment['from']['name']
                    comment_message = comment['message']
                    comment_id = comment['id']
                    if fbid_exists(comment_from_uid):
                        usr_dict = get_userdetails(comment_from_uid)
                        insert_comment(usr_dict, post_id, comment_id, comment_message, comment_from_uid, comment_from_name, comment_created_time, course_code, platform, platform_url)

def twitterusername_exists(screen_name):
    tw_id_exists = False
    if UserProfile.objects.filter(twitter_id=screen_name).count() > 0:
        tw_id_exists = True

    if tw_id_exists == False:
        tmp_user_dict = {'aneesha':'aneesha.bakharia@qut.edu.au','dannmallet':'dg.mallet@qut.edu.au', 'LuptonMandy': 'mandy.lupton@qut.edu.au', 'AndrewResearch':'andrew.gibson@qut.edu.au', 'KirstyKitto': 'kirsty.kitto@qut.edu.au' , 'skdevitt': 'kate.devitt@qut.edu.au' }
        if screen_name in tmp_user_dict:
            tw_id_exists = True
        else:
            tw_id_exists = True
    return tw_id_exists

def get_userdetails_twitter(screen_name):
    usr_dict = {'screen_name':screen_name}
    try:
        usr = UserProfile.objects.filter(twitter_id=screen_name).get()
    except UserProfile.DoesNotExist:
        usr = None

    if usr is not None:
        usr_dict['email'] = usr.user.email
        #usr_dict['lrs_endpoint'] = usr.ll_endpoint
        #usr_dict['lrs_username'] = usr.ll_username
        #usr_dict['lrs_password'] = usr.ll_password
    else:
        tmp_user_dict = {'aneesha':'aneesha.bakharia@qut.edu.au','dannmallet':'dg.mallet@qut.edu.au', 'LuptonMandy': 'mandy.lupton@qut.edu.au', 'AndrewResearch':'andrew.gibson@qut.edu.au', 'KirstyKitto': 'kirsty.kitto@qut.edu.au' , 'skdevitt': 'kate.devitt@qut.edu.au' }
        if screen_name in tmp_user_dict:
            usr_dict['email'] = tmp_user_dict[screen_name]
        else:
            usr_dict['email'] = 'test@gmail.com'
    return usr_dict

def fbid_exists(fb_id):
    fb_id_exists = False
    if UserProfile.objects.filter(fb_id=fb_id).count() > 0:
        fb_id_exists = True

    if fb_id_exists == False:
        tmp_user_dict = {10152850610457657:'kate.devitt@qut.edu.au',10153944872937892:'aneesha.bakharia@qut.edu.au', 10153189868088612: 'mandy.lupton@qut.edu.au', 856974831053214:'andrew.gibson@qut.edu.au'}
        if fb_id in tmp_user_dict:
            fb_id_exists = True
        else:
            fb_id_exists = True
    return fb_id_exists

def get_userdetails(fb_id):
    usr_dict = {'fb_id':fb_id}
    try:
        usr = UserProfile.objects.filter(fb_id=fb_id).get()
    except UserProfile.DoesNotExist:
        usr = None

    if usr is not None:
        usr_dict['email'] = usr.user.email
        #usr_dict['lrs_endpoint'] = usr.ll_endpoint
        #usr_dict['lrs_username'] = usr.ll_username
        #usr_dict['lrs_password'] = usr.ll_password
    else:
        tmp_user_dict = {10152850610457657:'kate.devitt@qut.edu.au',10153944872937892:'aneesha.bakharia@qut.edu.au', 10153189868088612: 'mandy.lupton@qut.edu.au', 856974831053214:'andrew.gibson@qut.edu.au'}
        if fb_id in tmp_user_dict:
            usr_dict['email'] = tmp_user_dict[fb_id]
        else:
            usr_dict['email'] = 'test@gmail.com'
    return usr_dict

def insert_post(usr_dict, post_id,message,from_name,from_uid, created_time, course_code, platform, platform_url, tags=[]):
    stm = socialmediabuilder.socialmedia_builder(verb='created', platform=platform, account_name=from_uid, account_homepage=platform_url, object_type='Note', object_id=post_id, message=message, timestamp=created_time, account_email=usr_dict['email'], user_name=from_name, course_code=course_code, tags=tags)
    jsn = ast.literal_eval(stm.to_json())
    stm_json = socialmediabuilder.pretty_print_json(jsn)
    lrs = LearningRecord(xapi=stm_json, course_code=course_code, verb='created', platform=platform, username=from_uid)
    lrs.save()

def insert_like(usr_dict, post_id, like_uid, like_name, message, course_code, platform, platform_url):
    stm = socialmediabuilder.socialmedia_builder(verb='liked', platform=platform, account_name=like_uid, account_homepage=platform_url, object_type='Note', object_id='post_id', message=message, account_email=usr_dict['email'], user_name=like_name, course_code=course_code)
    jsn = ast.literal_eval(stm.to_json())
    stm_json = socialmediabuilder.pretty_print_json(jsn)
    lrs = LearningRecord(xapi=stm_json, course_code=course_code, verb='liked', platform=platform, username=like_uid)
    lrs.save()

def insert_comment(usr_dict, post_id, comment_id, comment_message, comment_from_uid, comment_from_name, comment_created_time, course_code, platform, platform_url):
    stm = socialmediabuilder.socialmedia_builder(verb='commented', platform=platform, account_name=comment_from_uid, account_homepage=platform_url, object_type='Note', object_id=comment_id, message=comment_message, parent_id=post_id, parent_object_type='Note', timestamp=comment_created_time, account_email=usr_dict['email'], user_name=comment_from_name, course_code=course_code )
    jsn = ast.literal_eval(stm.to_json())
    stm_json = socialmediabuilder.pretty_print_json(jsn)
    lrs = LearningRecord(xapi=stm_json, course_code=course_code, verb='commented', platform=platform, username=comment_from_uid)
    lrs.save()

def insert_share(usr_dict, post_id, share_id, comment_message, comment_from_uid, comment_from_name, comment_created_time, course_code, platform, platform_url, tags=[]):
    stm = socialmediabuilder.socialmedia_builder(verb='shared', platform=platform, account_name=comment_from_uid, account_homepage=platform_url, object_type='Note', object_id=share_id, message=comment_message, parent_id=post_id, parent_object_type='Note', timestamp=comment_created_time, account_email=usr_dict['email'], user_name=comment_from_name, course_code=course_code, tags=tags )
    jsn = ast.literal_eval(stm.to_json())
    stm_json = socialmediabuilder.pretty_print_json(jsn)
    lrs = LearningRecord(xapi=stm_json, course_code=course_code, verb='shared', platform=platform, username=comment_from_uid)
    lrs.save()
