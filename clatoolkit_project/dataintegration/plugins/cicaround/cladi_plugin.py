from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin

from requests_oauthlib import OAuth1Session

from dataintegration.core.importer import *
from xapi.statement.builder import *

import os
from xapi.statement.xapi_settings import xapi_settings


class CAPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = xapi_settings.PLATFORM_CA
    platform_url = "https://ca.uts.edu.au"

    xapi_verbs = [xapi_settings.VERB_CREATED, xapi_settings.VERB_SHARED, 
                  xapi_settings.VERB_LIKED, xapi_settings.VERB_COMMENTED]
    xapi_objects = [xapi_settings.OBJECT_NOTE]

    user_api_association_name = 'CA Username' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Hashtags' # eg hashtags or a group name

    config_json_keys = ['app_key', 'app_secret', 'oauth_token', 'oauth_token_secret']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = [xapi_settings.OBJECT_NOTE]
    xapi_verbs_to_includein_verbactivitywidget = [xapi_settings.VERB_CREATED, xapi_settings.VERB_SHARED, 
                                                  xapi_settings.VERB_LIKED, xapi_settings.VERB_COMMENTED]

    def __init__(self):
        pass

    def perform_import(self, unit):

        instance = os.environ.get("CA_HOST")

        oauth = OAuth1Session(client_key=os.environ.get("CA_CLIENT_KEY"),
                              client_secret=os.environ.get("CA_CLIENT_SECRET"),
                              resource_owner_key=os.environ.get("CA_ACCESS_TOKEN_KEY"),
                              resource_owner_secret=os.environ.get("CA_ACCESS_TOKEN_SECRET"))

        self.get_posts(unit, oauth, instance)

    def get_posts(self, unit, oauth, instance):
        next_page = "{}/wp-json/clatoolkit-wp/v1/posts".format(instance)

        while next_page:
            r = oauth.get(next_page)
            result = r.json()

            for blog in result["posts"]:
                self.add_blog_posts(blog, unit)

            if "next_page" in result:
                next_page = result["next_page"]
            else:
                next_page = False

    def add_blog_posts(self, blog, unit):

        for post in blog["posts"]:

            try:
                user = User.objects.filter(email__iexact=post["author"]["email"])

                insert_post(user=user, post_id=post["guid"], message=post["post_content"],
                            created_time=post["post_date_gmt"], unit=unit, platform=self.platform, platform_url="")

                if "comments" in post:
                    for comment in post["comments"]:
                        try:
                            commenter = User.objects.filter(email__iexact=comment["comment_author_email"])

                            insert_comment(user=commenter, post_id=post["guid"], comment_id=comment["comment_guid"],
                                           comment_message=comment["comment_content"],
                                           comment_created_time=comment["comment_date_gmt"], unit=unit,
                                           platform=self.platform, platform_url="",
                                           parent_user=user)

                        except UserProfile.DoesNotExist:
                            # Don't store the comment if the author doesn't exist
                            pass

            except UserProfile.DoesNotExist:
                # Do nothing if the post author doesn't exist
                pass

    def get_verbs(self):
        return self.xapi_verbs

    def get_objects(self):
        return self.xapi_objects

registry.register(CAPlugin)