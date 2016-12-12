from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin

from dataintegration.core.di_utils import * #Formerly dataintegration.core.recipepermissions
from xapi.statement.builder import * #Formerly dataintegration.core.socialmediabuilder

import json
from bs4 import BeautifulSoup
from urllib2 import urlopen
import dateutil.parser


class ForumPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "Forum"
    platform_url = "http://2015.informationprograms.info/forums/"

    xapi_verbs = ['created', 'commented']
    xapi_objects = ['Note']

    user_api_association_name = 'Forum Username' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Forum Link' # eg hashtags or a group name

    config_json_keys = ['app_key', 'app_secret', 'oauth_token', 'oauth_token_secret']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Note']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'commented']

    def __init__(self):
        pass

    def perform_import(self, retrieval_param, course_code):

        forums  = self.get_forumlinks(self.platform_url)
        for forum in forums:
            forum_link = forum["forum_link"]
            forum_title = forum["forum_link"]
            forum_text = forum["forum_link"]
            forum_author = "admin"

            if username_exists(forum_author, course_code, self.platform):
                usr_dict = get_userdetails(forum_author, self.platform)
                insert_post(usr_dict, forum_link,forum_text,forum_author,forum_author, dateutil.parser.parse("1 July 2015 2pm"), course_code, self.platform, self.platform_url)

            topics = self.get_topiclinks(forum_link)
            for topic in topics:
                topic_link = topic["topic_link"]

                posts = self.get_posts(topic_link)
                for post in posts:
                    post_permalink = post["post_permalink"]
                    post_user_link = post["post_user_link"]
                    post_date = post["post_date"]
                    post_date = dateutil.parser.parse(post_date.replace(" at "," "))
                    post_content = post["post_content"]
                    post_user_link = post_user_link[:-1]
                    post_username = post_user_link[(post_user_link.rfind('/')+1):]
                    if username_exists(post_username, course_code, self.platform):
                        usr_dict = get_userdetails(post_username, self.platform)
                        insert_comment(usr_dict, forum_link, post_permalink, post_content, post_username, post_username, post_date, course_code, self.platform, self.platform_url, shared_username=forum_author)

    def make_soup(self, url):
        html = urlopen(url).read()
        return BeautifulSoup(html, "lxml")

    def get_forumlinks(self, url):
        forums = []

        soup = self.make_soup(url)
        forum_containers = soup.findAll("ul", "forum")
        for forum_item in forum_containers:
            forum_link = forum_item.find("a", "bbp-forum-title").attrs['href']
            forum_title = forum_item.find("a", "bbp-forum-title").string
            forum_text = forum_item.find("div", "bbp-forum-content").string
            if forum_text is None:
                forum_text = ""
            forum_user = "admin"
            forum_dict = {'forum_link': forum_link, 'forum_title': forum_title, 'forum_text': forum_text }
            forums.append(forum_dict)
        return forums

    def get_topiclinks(self, url):
        topics = []

        soup = self.make_soup(url)
        topic_containers = soup.findAll("ul", "topic")
        for topic_item in topic_containers:
            topic_link = topic_item.find("a", "bbp-topic-permalink").attrs['href']
            topic_title = topic_item.find("a", "bbp-topic-permalink").string
            topic_author = topic_item.find("a", "bbp-author-avatar").attrs['href']
            topic_dict = {'topic_link': topic_link, 'topic_title': topic_title, 'topic_author': topic_author }
            topics.append(topic_dict)

        return topics

    def get_posts(self, topic_url):
        posts = []

        soup = self.make_soup(topic_url)

        posts_container = soup.findAll("ul", "forums")

        post_containers = posts_container[0].findAll("li")
        for post in post_containers:
            if post.find("span", "bbp-reply-post-date") is not None:
                post_date = post.find("span", "bbp-reply-post-date").string
                post_permalink = post.find("a", "bbp-reply-permalink").attrs['href']
                post_user_link = post.find("a", "bbp-author-avatar").attrs['href']
                post_content = str(post.find("div", "bbp-reply-content"))
                post_dict = {'post_permalink': post_permalink, 'post_user_link': post_user_link, 'post_date': post_date, 'post_content': post_content }
                posts.append(post_dict)

        return posts

registry.register(ForumPlugin)
