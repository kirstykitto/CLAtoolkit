__author__ = 'zak'

from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin, DIAuthomaticPluginMixin
from dataintegration.core.socialmediarecipebuilder import *
from dataintegration.core.recipepermissions import *
import json
import dateutil.parser
from authomatic.providers import oauth2
import requests
import os

#Trello pylib
from trello import TrelloClient

#OAuth for trello
from requests_oauthlib import OAuth1Session


class TrelloPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "trello"
    platform_url = "http://www.trello.com/"

    #created for "create" actions
    #added for "add" actions
    #updated for "update" actions
    #commented for card "comment" actions
    xapi_verbs = ['created', 'added', 'updated', 'commented']

    #Note for "commented" actions
    #Task for "created", "added", "updated", and "commented" actions
    #Collection for any "created", "added", "updated" List actions (tentative use)
    xapi_objects = ['Note', 'Task', 'Collection']

    user_api_association_name = 'Trello UID' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Board ID' # eg hashtags or a group name

    config_json_keys = ['consumer_key', 'consumer_secret']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Note']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'shared', 'liked', 'commented']

    #for OAuth1 authentication
    token_request_url = ''

    def __init__(self):
        #Load api_config.json and convert to dict
        config_file = os.path.join(os.path.dirname(__file__), 'api_config.json')

        with open(config_file) as data_file:
            self.api_config_dict = json.load(data_file)

    def perform_import(self, retreival_param, course_code):
        from clatoolkit.models import ApiCredentials
        #Set up trello auth and API
        self.usercontext_storage_dict = json.load(ApiCredentials.objects.get(platform=retreival_param).credentials_json)
        token = self.usercontext_storage_dict['token']
        s_token = self.usercontext_storage_dict['token_secret']

        self.TrelloCient = TrelloClient(
            api_key=self.api_config_dict['api_key'],
            api_secret=self.api_config_dict['api_secret'],
            token=token,
            token_secret=s_token
        )

        #Get user-registered board in trello
        trello_board = self.TrelloCient.get_board(retreival_param)

        #Get boards activity/action feed
        trello_board.fetch_actions() #fetch_actions() collects actions feed and stores to trello_board.actions

        self.import_TrelloActivity(trello_board.actions, course_code)

    def import_TrelloActivity(self, feed, course_code):
        #User needs to sign up username and board (board can be left out but is needed)

        for action in list(feed):
            action = json.load(action)

            u_id = action['idMemberCreator']
            author = action['memberCreator']['username']
            type = action['type'] #commentCard, updateCard, createList,etc
            data = action['data']
            date = action['date']
            board_name = data['board']['name']

            #Get all 'commented' verb actions
            if (type is 'commentCard'):
                #do stuff
                target_obj_id = data['card']['shortLink']
                #date
                comment_from_uid = u_id
                comment_from_name = author
                comment_message = data['text']
                comment_id = action['id']

                if username_exists(comment_from_uid, course_code, self.platform):
                    usr_dict = get_userdetails(comment_from_uid, self.platform)
                    insert_comment(usr_dict, target_obj_id, comment_id,
                                   comment_message, comment_from_uid,
                                   comment_from_name, date, course_code,
                                   self.platform, self.platform_url)

            #Get all 'create' verb actions
            if (type in ['createCard']): #, 'createList']):
                #date
                #list_id = data['list']['id']
                task_id = data['card']['shortlink']
                task_name = data['card']['name']

                if username_exists(u_id, course_code, self.platform):
                    usr_dict = get_userdetails(u_id, self.platform)
                    insert_task(usr_dict, task_id, task_name, u_id, author, date,
                                course_code, self.platform, self.platform_url) #, list_id=list_id)


            #Get all 'add' verbs (you tecnically aren't *creating* an attachment on
            #a card so....)
            if (type in
                ['addAttachmentToCard', 'addMemberToBoard',
                 'emailCard', 'addCheckListToCard'
                 , 'addMemberToCard']):

            #Get all 'updated' verbs
            if (type in
                ['updateCheckItemStateOnCard', 'updateBoard',
                 'updateCard:closed', 'updateCard:desc', 'updateCard:idList',
                 'updateCard:name', 'updateCheckList', 'updateList:closed',
                 'updateList:name', 'updateMember']):







"""
        authors = self.usercontext_storage_dict['members']

        #all labels existing in the trello board
        labels = board.get_labels()


        #************************************#
        #       Extract Info logic           #
        #                                    #
        #************************************#
        for card in trello_board_cards:
            create_date = card.card_created_date

            #Card name is generally to activity to be completed
            card_name = card.name

            #Card labels
            card_labels = None
            if len(card.list_labels) is not 0:
                card_labels = card.list_labels

            #Card Description - card_desc
            card_desc = None
            if card.description is not None and not '':
                card_desc = card.description

            #Last activity - card_activity
            card_activity = None
            if card.date_last_activity is not None:
                card_activity = card.date_last_activity

            #Card Comments -  card_comments
            card_comments = None
            if len(card.comments) is not 0:
                card_comments = card.comments

            #Card Checklists = card_checklists
            card_checklists = None
            if len(card.checklists) is not 0:
                card_checklists = card_checklists
"""












