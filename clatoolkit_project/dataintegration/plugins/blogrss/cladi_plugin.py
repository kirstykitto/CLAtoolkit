from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin
from dataintegration.core.socialmediarecipebuilder import *
from dataintegration.core.recipepermissions import *
import json
from bs4 import BeautifulSoup
from urllib2 import urlopen
import dateutil.parser
import feedparser
import urlparse
import urllib
import urllib2


'''
This plugin is specifically designed for the Kate Davies unit that is using Wordpress with multiple
blog sites in Sem 1, 2016.
Wordpress does have a rest api but I could not the rest urls to work - maybe the version of Wordpress
is not recent or the API is not enabled or an authenticated user is required (oauth). I am not sure.
Some info on the rest api can be found here:
http://code.tutsplus.com/tutorials/wp-rest-api-retrieving-data--cms-24694
It might be useful to port this plugin to the restful api later on.
For Sem 1, 2016 however a plugin was needed immediately at late notice.
The multisite has an activity feed but this was not useful because:
- blog posts and comments are truncated
- no reply to details in the comments
- other feed activity would need to be filtered by searching for text
  eg is friends with or joined
- hard to determine the username of the person making the post or comment

To get the data into CLAToolkit the following is implemented in this plugin:
- Get list of all member blogs. This is listed in html on an ajax paged ui. BeautifulSoup is used to
  get this data - post requests need to be made to get the other pages. #json_array_elements
- For each member blog url, a rss posts feed and a comments feed is processed. feedparser is used.
- ... and there is a lot of fun code to match users to their usernames. #joy of not having an api

'''

class BlogrssPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "Blog"
    platform_url = "http://2016.informationprograms.info/"

    xapi_verbs = ['created', 'commented']
    xapi_objects = ['Article', 'Note']

    user_api_association_name = 'Blog Username'
    unit_api_association_name = 'RSS Feed URL'

    config_json_keys = []

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Note', 'Article']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'commented']

    def __init__(self):
        pass

    def perform_import(self, retrieval_param, course_code):
        memberblog_urls = self.get_allmemberblogurls(retrieval_param)
        displayname_username_dict = {}
        for memberblog_url in memberblog_urls:
            member_blogfeed = memberblog_url + 'feed/'
            #print 'getting memberblog feed: ' + member_blogfeed

            temp_dict = self.insert_blogposts(member_blogfeed, course_code)
            displayname_username_dict.update(temp_dict)
        for memberblog_url in memberblog_urls:
            member_commentfeed = memberblog_url + 'comments/feed/'
            self.insert_blogcomments(member_commentfeed, course_code, displayname_username_dict)

    def get_allmemberblogurls(self, memberlist_url, max_pages=4):

        #Ajax Handler for 2016 blog site
        base_url = 'http://2016.informationprograms.info/wp-admin/admin-ajax.php'

        #Parameters for AJAX pagination
        data = {'action': 'blogs_filter',
                'cookie': 'bp-activity-oldestpage%253D1',
                'object': 'blogs',
                'search_terms' : '',
                'page' : 1,
                'template': ''
        }
        #http://2016.socialtechnologi.es/wp-admin/admin-ajax.php?action=blogs_filter&cookie=bp-activity-oldestpage%253D1&object=blogs&search_terms=&page=1&template=

        memberblog_urls = []
        # try to get all pages of blog members
        #eg http://stackoverflow.com/questions/12519193/using-python-urllib2-to-send-post-request-and-get-response
        while (data['page'] <= max_pages):
            url_data = urllib.urlencode(data)
            req = urllib2.Request(base_url, url_data)
            html = urlopen(req,timeout=300).read()
            soup = BeautifulSoup(html, "lxml")

            blog_containers = soup.findAll("div", class_="item-avatar")
            for blog_item in blog_containers:
                blog_link = blog_item.find("a").attrs['href']

                memberblog_urls.append(blog_link)

            data['page'] = data['page'] + 1

        #print memberblog_urls
        #print "BLOGS SCRAPED: %s" % len(memberblog_urls)
        #return ['http://2016.socialtechnologi.es/moonlo/']
        return memberblog_urls

    def insert_blogposts(self, blogfeed, course_code):
        d = feedparser.parse(blogfeed)
        displayname_username_dict = {}
        #print d
        try:
            blogurl = d['feed']['link']
            slash_pos = blogurl.rfind('/')
            blog_url_name = blogurl[slash_pos+1:]

            #print username

            #dict to stored blog display name with url name

            #print d.feed.subtitle
            #print d.version
            #print d.headers.get('content-type')
            #print len(d['entries'])
            for post in d.entries:
                link = post.link
                message = post.title + " " + post.content[0]['value']
                blog_display_name = post.author
                post_date = dateutil.parser.parse(post.published)
                tags_dict_list = post.tags
                tags = []
                for tag_dict in tags_dict_list:
                    term = tag_dict['term']
                    tags.append(term)

                if blog_display_name not in displayname_username_dict:
                    displayname_username_dict[blog_display_name] = blog_url_name

                #print "Does " + blog_url_name + "exist in Toolkit?: " + username_exists(displayname_username_dict[blog_display_name], course_code, self.platform)
                if username_exists(displayname_username_dict[blog_display_name], course_code, self.platform):
                    usr_dict = get_userdetails(displayname_username_dict[blog_display_name], self.platform)
                    insert_blogpost(usr_dict, link, message, get_username_fromsmid(blog_url_name,self.platform), blog_display_name, post_date, course_code, self.platform, self.platform_url, tags=tags)
        except KeyError:
            pass

        return displayname_username_dict

    def insert_blogcomments(self, member_commentfeed, course_code, displayname_username_dict):
        d = feedparser.parse(member_commentfeed)

        for post in d.entries:
            link = post.link
            slash_pos = post.link.rfind("/")
            parent_link = post.link[:slash_pos+1]
            path = urlparse.urlparse(parent_link).path
            parent_username = path.split('/')[1]
            message = post.title + " " + post.content[0]['value']
            author = post.author
            post_date = dateutil.parser.parse(post.published)
            if author != "Anonymous" and author in displayname_username_dict:
                post_username = displayname_username_dict[author]
                post_date = dateutil.parser.parse(post.published)

                if username_exists(post_username, course_code, self.platform):
                    usr_dict = get_userdetails(post_username, self.platform)
                    insert_comment(usr_dict, parent_link, link, message, post_username, author, post_date, course_code, self.platform, self.platform_url, shared_username=parent_username)

registry.register(BlogrssPlugin)


