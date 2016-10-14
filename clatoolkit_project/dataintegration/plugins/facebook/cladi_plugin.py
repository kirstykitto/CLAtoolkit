from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin, DIAuthomaticPluginMixin
from dataintegration.core.socialmediarecipebuilder import *
from dataintegration.core.recipepermissions import *
import json
import dateutil.parser
from authomatic.providers import oauth2
import requests
import os


class FacebookPlugin(DIBasePlugin, DIPluginDashboardMixin, DIAuthomaticPluginMixin):

    platform = "facebook"
    platform_url = "http://www.facebook.com/"

    xapi_verbs = ['created', 'shared', 'liked', 'commented']
    xapi_objects = ['Note']

    user_api_association_name = 'Facebook UID' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Group ID' # eg hashtags or a group name

    config_json_keys = ['consumer_key', 'consumer_secret']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Note']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'shared', 'liked', 'commented']

    #from AuthomaticPluginMixin
    authomatic_config_json = {}

    authomatic_config_key = 'fb'
    authomatic_secretkey = os.environ.get("FACEBOOK_AUTHOMATIC_SECRET_KEY")

    def __init__(self):
        #from AuthomaticPluginMixin
        self.authomatic_config_json = {
            # Auth information for Facebook App
            'fb': {
                'class_': oauth2.Facebook,
                'consumer_key': os.environ.get("FACEBOOK_CONSUMER_KEY"),
                'consumer_secret': os.environ.get("FACEBOOK_CONSUMER_SECRET"),

                'scope': ['user_about_me', 'email', 'user_managed_groups'],
                },
            }

        self.authomatic_config_key = 'fb'

        self.authomatic_secretkey = str(os.environ.get("FACEBOOK_AUTHOMATIC_SECRET_KEY"))

    def perform_import(self, retrieval_param, unit, authomatic_result):
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

        url = 'https://graph.facebook.com/v2.8/'+retrieval_param+'/feed'
        params = {"fields": "created_time,from,message,likes,comments{created_time,from,message}"}
        access_response = authomatic_result.provider.access(url, params=params)
        data = access_response.data.get('data')
        paging = access_response.data.get('paging')
        while True:
            try:
                self.insert_facebook_lrs(data, unit)
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

    def insert_facebook_lrs(self, fb_feed, unit):
        """
        1. Parses facebook feed
        2. Uses construct_tincan_statement to format data ready to send for the LRS
        3. Sends to the LRS and Saves to postgres json field
        :param fb_feed: Facebook Feed as dict
        :param unit: A UnitOffering object
        :return:
        """

        for post in fb_feed:
            if 'message' in post:
                created_time = dateutil.parser.parse(post['created_time'])
                from_uid = post['from']['id']
                post_id = post['id']
                message = post['message']

                print("Post: {}".format(message))

                if username_exists(from_uid, unit, self.platform):
                    user = get_user_from_screen_name(from_uid, self.platform)
                    print("User {} exists".format(user.first_name))

                    insert_post(user, post_id, message, created_time, unit, self.platform, self.platform_url)

                    if 'likes' in post:
                        for like in post['likes']['data']:
                            like_uid = like['id']

                            if username_exists(like_uid, unit, self.platform):
                                like_user = get_user_from_screen_name(from_uid, self.platform)
                                insert_like(like_user, post_id, message, unit, self.platform, created_time, parent_user=user)

                    if 'comments' in post:
                        for comment in post['comments']['data']:
                            comment_created_time = comment['created_time']
                            comment_from_uid = comment['from']['id']
                            comment_message = comment['message']
                            comment_id = comment['id']

                            if username_exists(comment_from_uid, unit, self.platform):
                                comment_user = get_user_from_screen_name(comment_from_uid, self.platform)
                                insert_comment(comment_user, post_id, comment_id, comment_message, comment_created_time,
                                               unit, self.platform, self.platform_url, parent_user=user)


registry.register(FacebookPlugin)

