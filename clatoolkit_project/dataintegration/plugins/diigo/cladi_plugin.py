from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin

from dataintegration.core.di_utils import * #Formerly dataintegration.core.recipepermissions
from xapi.statement.builder import * #Formerly dataintegration.core.socialmediabuilder

import json
import dateutil.parser
import os

class DiigoPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "Diigo"
    platform_url = "http://www.diigo.com/"

    xapi_verbs = ['created', 'commented']
    xapi_objects = ['Link']

    user_api_association_name = 'Diigo Username' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Diigo Tags' # eg hashtags or a group name

    config_json_keys = ['user', 'password', 'apikey']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Bookmark']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'commented']

    def __init__(self):
        pass

    def perform_import(self, retrieval_param, course_code):

        # Setup Twitter API Keys
        user = os.environ.get("DIIGO_USER")
        password = os.environ.get("DIIGO_PASSWORD")
        apikey = os.environ.get("DIIGO_API_KEY")

        # call api and process bookmarks here
        # retrieval_param will contain a single tag
        # for each insert check if user exists and then get user details
        # then process returned json and call insert_link or insert_comment
        '''
        if username_exists(username, course_code, self.platform):
            usr_dict = get_userdetails(username, self.platform)

            insert_bookmark(usr_dict, post_id,message,fullname,username, timestamp, course_code, self.platform, self.platform_url, tags=tags)
            insert_comment(usr_dict, forum_link, post_permalink, post_content, post_username, post_username, post_date, course_code, self.platform, self.platform_url, shared_username=forum_author)
        '''

registry.register(DiigoPlugin)
