from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin
from dataintegration.core.socialmediarecipebuilder import *
from dataintegration.core.recipepermissions import *
import json
import dateutil.parser
from twython import Twython
import os

class TwitterPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "Twitter"
    platform_url = "http://www.twitter.com/"

    xapi_verbs = ['created', 'shared', 'liked', 'commented']
    xapi_objects = ['Note']

    user_api_association_name = 'Twitter Username' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Hashtags' # eg hashtags or a group name

    config_json_keys = ['app_key', 'app_secret', 'oauth_token', 'oauth_token_secret']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Note']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'shared', 'liked', 'commented']

    def __init__(self):
        # Load api_config.json and convert to dict
        config_file = os.path.join(os.path.dirname(__file__), 'api_config.json')
        with open(config_file) as data_file:
            self.api_config_dict = json.load(data_file)

    def perform_import(self, retrieval_param, course_code):

        # Setup Twitter API Keys
        app_key = self.api_config_dict['app_key']
        app_secret = self.api_config_dict['app_secret']
        oauth_token = self.api_config_dict['oauth_token']
        oauth_token_secret = self.api_config_dict['oauth_token_secret']

        twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

        count = 0
        next_max_id = None
        results = None
        while True:
            try:
                if count==0:
                    results = twitter.search(q=retrieval_param,count=100, result_type='mixed')
                else:
                    results = twitter.search(q=retrieval_param,count=100,max_id=next_max_id, result_type='mixed')

                for tweet in results['statuses']:
                    self.insert_tweet(tweet, course_code)

                if 'next_results' not in results['search_metadata']:
                        break
                else:
                    next_results_url_params    = results['search_metadata']['next_results']
                    next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
                count += 1
            except KeyError:
                    # When there are no more pages (['paging']['next']), break from the
                    # loop and end the script.
                    break

    def insert_tweet(self, tweet, course_code):
        message = tweet['text']
        timestamp = dateutil.parser.parse(tweet['created_at'])
        username = tweet['user']['screen_name']
        fullname = tweet['user']['name']
        post_id = self.platform_url + username + '/status/' + str(tweet['id'])
        retweeted = False
        retweeted_id = None
        retweeted_username = None
        if 'retweeted_status' in tweet:
            retweeted = True
            retweeted_id = self.platform_url + username + '/status/' + str(tweet['retweeted_status']['id'])
            retweeted_username = tweet['retweeted_status']['user']['screen_name']
            # get hashtags
        tags = []
        hashtags = tweet['entities']['hashtags']
        for hashtag in hashtags:
            tag = hashtag['text']
            tags.append(tag)
        # get @mentions
        # favorite_count
        mentions = []
        atmentions = tweet['entities']['user_mentions']
        for usermention in atmentions:
            mention = "@" + str(usermention['screen_name'])
            tags.append(mention)
        #print post_id
        #print twitterusername_exists(username, course_code)
        if username_exists(username, course_code, self.platform):
            usr_dict = get_userdetails(username, self.platform)
            if retweeted:
                insert_share(usr_dict, post_id, retweeted_id, message,username,fullname, timestamp, course_code, self.platform, self.platform_url, tags=tags, shared_username=retweeted_username)
            else:
                insert_post(usr_dict, post_id,message,fullname,username, timestamp, course_code, self.platform, self.platform_url, tags=tags)

registry.register(TwitterPlugin)
