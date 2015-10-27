from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep

#BASE_URL = "http://2015.informationprograms.info/forums/topic/who-am-i-2/"
BASE_URL = "http://2015.informationprograms.info/forums/"
#BASE_URL = "http://2015.informationprograms.info/forums/forum/assignment-1/"

def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, "lxml")

def get_forumlinks(url):
    forums = []

    soup = make_soup(url)
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
        #print forums

    return forums

def get_topiclinks(url):
    topics = []

    soup = make_soup(url)
    topic_containers = soup.findAll("ul", "topic")
    for topic_item in topic_containers:
        topic_link = topic_item.find("a", "bbp-topic-permalink").attrs['href']
        topic_title = topic_item.find("a", "bbp-topic-permalink").string
        topic_author = topic_item.find("a", "bbp-author-avatar").attrs['href']
        #print topic_title, topic_link, topic_author[0:-1]
        topic_dict = {'topic_link': topic_link, 'topic_title': topic_title, 'topic_author': topic_author }
        topics.append(topic_dict)

    return topics

def get_posts(topic_url):
    posts = []

    soup = make_soup(topic_url)

    posts_container = soup.findAll("ul", "forums")

    post_containers = posts_container[0].findAll("li")
    for post in post_containers:
        if post.find("span", "bbp-reply-post-date") is not None:
            post_date = post.find("span", "bbp-reply-post-date").string
            post_permalink = post.find("a", "bbp-reply-permalink").attrs['href']
            post_user_link = post.find("a", "bbp-author-avatar").attrs['href']
            post_content_div = post.find("div", "bbp-reply-content")
            post_content = post_content_div.find("p").string
            post_dict = {'post_permalink': post_permalink, 'post_user_link': post_user_link, 'post_date': post_date, 'post_content': post_content }
            posts.append(post_dict)

    return posts

def ingest_forum(url):
    forums  = get_forumlinks(url)
    for forum in forums:
        forum_link = forum["forum_link"]
        forum_title = forum["forum_link"]
        forum_text = forum["forum_link"]
        forum_author = "admin"
        # insert forum in xapi

        topics = get_topiclinks(forum_link)
        for topic in topics:
            topic_link = topic["topic_link"]

            posts = get_posts(topic_link)
            for post in posts:
                post_permalink = post["post_permalink"]
                post_user_link = post["post_user_link"]
                post_date = post["post_date"]
                post_date = post_date.replace(" at "," ")
                post_content = post["post_content"]
                post_username = post_user_link[post_user_link.rfind('/'):-1]
                # insert each post in xapi
                print post_username, post_date

ingest_forum(BASE_URL)

#get_forumlinks(BASE_URL)

#get_topiclinks(BASE_URL)

#get_posts(BASE_URL)

#https://gist.github.com/gjreda/f3e6875f869779ec03db
