from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from twython import Twython

from fb_data.models import UserProfile
from tw_data import socialmedia_builder


# from socialmedia_builder import *

logger = get_task_logger(__name__)

from tincan import (
    RemoteLRS
)


@shared_task
def send_twitter_data_to_lrs(account, sent_hashtag):
    """
    Sends formatted data to LRS
    1. Parses twitter feed
    2. Uses construct_tincan_statement to format data ready to send for the LRS
    3. Sends to the LRS
    :param data: Graph API query data
    :param paging: Graph API query paging data: next page (if there is one)
    :param html_response: Current HTML response to send to web browser
    :return:
    """
    statements = []

    # # Bulk send statements to main LRS
    lrs = RemoteLRS(
        endpoint="http://54.206.43.109/data/xAPI/",
        version="1.0.1",  # 1.0.1 | 1.0.0 | 0.95 | 0.9
        username="7d09242b9160fac074363db8a8f501a1b0635ad7",
        password="aa9610b64cfab20e9f559da63d8960ed56b65134"
    )
    # response = lrs.save_statements(statements)
    # Setup API Keys
    app_key = "barKrgroD3LcyHRwehvaiv1Zu"
    app_secret = "v6awGTCTP6wNJNhMPzmUzuIi1bAfNuoFOuPq1LXoCNjyqOIUki"
    oauth_token = "1851621-4eTSnqZehoeVBWqUxGERiPKjnTsVEFaJ77MnTWKRfo"
    oauth_token_secret = "4ZoEKJ9hnbviCuFtfGq2hBdCsfuX6eyqvvkbFGEeytE0U"

    twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

    # Add hash to start of hashtag
    # hashtag = '#' + hashtag

    # see https://dev.twitter.com/rest/reference/get/search/tweets for search options

    results = twitter.search(q=account, count=10000)
    for tweet in results['statuses']:
        # body = tweet['text']
        # id = tweet['id']
        # timestamp = tweet['created_at']
        # location = tweet['user']['location']
        # userid = tweet['user']['id']
        # username = tweet['user']['screen_name']
        # print id, timestamp, location, userid, username, body
        hashtags = []
        for hashtag in tweet['entities']['hashtags']:
            if sent_hashtag == hashtag['text']:
                # Check to see if tweet contains hashtag and it isn't a retweet
                # and int(tweet['retweet_count']) == 0
                if UserProfile.objects.filter(fb_id=comment[u'from'][u'id']).count() > 0:
                    personal_lrs = UserProfile.objects.filter(fb_id=comment[u'from'][u'id']).get()
                    email = personal_lrs.user.email
                stm = socialmedia_builder.socialmedia_builder(verb='created',
                                                              platform='Twitter',
                                                              account_name=tweet['user']['screen_name'],
                                                              object_type='Note',
                                                              object_id='https://www.twitter.com/' +
                                                                        tweet['user']['screen_name'] +
                                                                        '/status/' + str(tweet['id']),
                                                              message=tweet['text'],
                                                              timestamp=tweet['created_at'],
                                                              tags=hashtags,
                                                              account_homepage="www.placeholder.com")
                print tweet['text']
                response = lrs.save_statement(stm)
                # TODO: paging
                print response.data
                print response.success
                print response.content


def get_next_feed(paging, html_response):
    """
    Check if there is any more data, if so grab next page and call send_twitter_data_to_lrs.
    :param paging: Paging URL from Facebook API request
    :param html_response: Current HTML for page
    :return:
    """
    # next_feed = requests.get(paging[u'next'])
    # next_feed_json = json.loads(next_feed.content)
    # data = next_feed_json[u'data']
    # if 'paging' in next_feed_json:
    #     print "Fetching next page"
    #     paging = next_feed_json[u'paging']
    # # Start formatting and sending next page to the LRS
