from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger

from fb_data.models import UserProfile

logger = get_task_logger(__name__)

import json

import requests
from tincan import (
    RemoteLRS,
    Statement
)

@shared_task
def send_data_to_lrs(data, paging, html_response):
    """
    Sends formatted data to LRS
    1. Parses facebook feed
    2. Uses construct_tincan_statement to format data ready to send for the LRS
    3. Sends to the LRS
    :param data: Graph API query data
    :param paging: Graph API query paging data: next page (if there is one)
    :param html_response: Current HTML response to send to web browser
    :return:
    """
    statements = []
    for post in data:
        if 'message' in post:
            # Check to see if user has signed up for data integration, if so - format and send their data.
            if UserProfile.objects.filter(fb_id=post[u'from'][u'id']).count() > 0:
                personal_lrs = UserProfile.objects.filter(fb_id=post[u'from'][u'id']).get()
                email = personal_lrs.user.email
                # Debug:
                print 'post:' + post[u'message']
                statements.append(construct_tincan_statement(post, 'post', email))
                # Send to user's personal LRS
                lrs = RemoteLRS(
                    endpoint=personal_lrs.ll_endpoint,
                    version ="1.0.1",
                    username=personal_lrs.ll_username,
                    password=personal_lrs.ll_password
                )
                response = lrs.save_statement(construct_tincan_statement(post, 'post', email))
                if 'comments' in post:
                    for comment in post[u'comments'][u'data']:
                        # Check to see if user has signed up for data integration, if so - format and send their data.
                        if UserProfile.objects.filter(fb_id=comment[u'from'][u'id']).count() > 0:
                            personal_lrs = UserProfile.objects.filter(fb_id=comment[u'from'][u'id']).get()
                            email = personal_lrs.user.email
                            # Debug:
                            print 'comment:' + comment[u'message']
                            statements.append(construct_tincan_statement(comment, 'comment', email))

                            # Send to user's personal LRS
                            lrs = RemoteLRS(
                                endpoint=personal_lrs.ll_endpoint,
                                version ="1.0.1",
                                username=personal_lrs.ll_username,
                                password=personal_lrs.ll_password
                            )
                            response = lrs.save_statement(construct_tincan_statement(comment, 'comment', email))
                            # Debug:
                            # print response.success
                            # print response.data
        # if 'likes' in post:
        #     for like in post[u'likes'][u'data']:
        #         # Check to see if user has signed up for data integration, if so - format and send their data.
        #         if UserProfile.objects.filter(fb_id=like[u'id']).count() > 0:
        #             personal_lrs = UserProfile.objects.filter(fb_id=like[u'id']).get()
        #             email = personal_lrs.user.email
        #             # Debug:
        #             print 'like:' + like[u'name']
        #             statements.append(construct_tincan_statement(like, 'like', email))
        #
        #             # Send to user's personal LRS
        #             lrs = RemoteLRS(
        #                 endpoint=personal_lrs.ll_endpoint,
        #                 version ="1.0.1",
        #                 username=personal_lrs.ll_username,
        #                 password=personal_lrs.ll_password
        #             )
        #             response = lrs.save_statement(construct_tincan_statement(like, 'like', email))
                    # Debug:
                    # print response.success
                    # print response.data
            # TODO: Add like paging support (if there is more than one page of likes)
            # TODO: Add comment like gathering:
            # http://stackoverflow.com/questions/16955653/facebook-graph-api-how-to-get-likes-for-comment

    # Bulk send statements to main LRS
    lrs = RemoteLRS(
        endpoint="http://54.206.43.109/data/xAPI/",
        version="1.0.1",  # 1.0.1 | 1.0.0 | 0.95 | 0.9
        username="954e556adaa5e1b4d21becd4dce24ee238c71038",
        password="db5bdd6cc9b8475fdbbe023dad1a92ae8233ba8c"
    )
    response = lrs.save_statements(statements)

    if paging:
        get_next_feed(paging, html_response)
    else:
        return html_response
    # TODO Non-text posts

def construct_tincan_statement(data, type, email):
    """
    Format tincan statement for sending to LRS
    :param data: API data
    :param type: Type of statement (post, comment, like)
    :param email: Email of sender
    :return:
    """
    if type == 'post':
        verb_id = 'http://activitystrea.ms/schema/1.0/create'
        verb_display_name = 'created'
        object_id = 'http://adlnet.gov/exapi/activities/media' # Note - short text statement, long text - article,
        object_display_name = 'post'
        from_name = data[u'from'][u'name']
        message = data[u'message']
    elif type == 'comment':
        verb_id = 'http://activitystrea.ms/schema/1.0/comment'
        verb_display_name = 'commented on'
        object_id = 'http://adlnet.gov/exapi/activities/comment'
        object_display_name = 'comment'
        from_name = data[u'from'][u'name']
        message = data[u'message']
    # elif type == 'like':
    #     verb_id = 'http://activitystrea.ms/schema/1.0/like'
    #     verb_display_name = 'liked'
    #     object_id = 'http://adlnet.gov/exapi/activities/post'
    #     object_display_name = 'post'
    #     from_name = data[u'name']
    #     message = "Like"
    else:
        print "Unsupported statement type."
        return "ERROR"
    statement = Statement(
        {
            "actor": {
                "mbox": "mailto:" + email,
                "name": from_name
            },
            "verb": {
                "id":verb_id,
                "display": {
                    "en-US": verb_display_name
                }
            },
            "object": {
                "id": object_id,
                "definition": {
                    "name": {
                        "en-US": object_display_name
                    }
                }

            },
            "result": {
                "response":
                    message

            },
            "timestamp": data[u'created_time']
        }
    )
    return statement

def get_next_feed(paging, html_response):
    """
    Check if any more data in feed, if so grab next page and call send_data_to_lrs.
    :param paging: Paging URL from Facebook API request
    :param html_response: Current HTML for page
    :return:
    """
    next_feed = requests.get(paging[u'next'])
    next_feed_json = json.loads(next_feed.content)
    data = next_feed_json[u'data']
    if 'paging' in next_feed_json:
        print "Fetching next page"
        paging = next_feed_json[u'paging']
    # Start formatting and sending next page to the LRS
    send_data_to_lrs(data, paging, html_response)
