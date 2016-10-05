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
from common.common import ClaUserUtil, CLRecipe


class TrelloPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "trello"
    platform_url = "http://www.trello.com/"

    #created for "create" actions
    #added for "add" actions
    #updated for "update" actions
    #commented for card "comment" actions
    xapi_verbs = ['created', 'added', 'updated', 'commented', 'closed', 'opened']

    #Note for "commented" actions
    #Task for "created", "added", "updated", and "commented" actions
    #Collection for any "created", "added", "updated" List actions (tentative use)
    xapi_objects = ['Note', 'Task', 'Collection', 'Person', 'File', 'checklist-item', 'checklist']

    user_api_association_name = 'Trello UID' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Board ID' # eg hashtags or a group name

    config_json_keys = ['consumer_key', 'consumer_secret']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Note']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'shared', 'liked', 'commented']

    #for OAuth1 authentication
    token_request_url = ''

    # Trello action type
    # Note: MoveCard, CloseCard, OpenCard are created for the toolkit to identify what users really did
    #       (The original action type of moving/closing/opening card are all same: updateCard)
    ACTION_TYPE_COMMENT_CARD = 'commentCard'
    ACTION_TYPE_CREATE_CARD = 'createCard'
    ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD = 'updateCheckItemStateOnCard'
    ACTION_TYPE_UPDATE_CARD = 'updateCard'
    ACTION_TYPE_ADD_ATTACHMENT_TO_CARD = 'addAttachmentToCard'
    ACTION_TYPE_ADD_CHECKLIST_TO_CARD = 'addChecklistToCard'
    ACTION_TYPE_ADD_MEMBER_TO_CARD = 'addMemberToCard'
    ACTION_TYPE_MOVE_CARD = 'moveCard'
    ACTION_TYPE_CLOSE_CARD = 'closeCard'
    ACTION_TYPE_OPEN_CARD = 'openCard'


    def __init__(self):
       pass

    #retreival param is the user_id
    def perform_import(self, retreival_param, course_code, token=None):
        #from clatoolkit.models import ApiCredentials
        #Set up trello auth and API
        #self.usercontext_storage_dict = json.load(ApiCredentials.objects.get(platform=retreival_param).credentials_json)

        self.TrelloCient = TrelloClient(
            api_key=os.environ.get("TRELLO_API_KEY"),
            #api_secret=self.api_config_dict['api_secret'],
            token=token
        )

        #Get user-registered board in trello
        trello_board = self.TrelloCient.get_board(retreival_param)

        #Get boards activity/action feed
        trello_board.fetch_actions('all') #fetch_actions() collects actions feed and stores to trello_board.actions

        #self.key = trello_board.api_key
        #self.token = trello_board.resource_owner_key

        self.import_TrelloActivity(trello_board.actions, course_code)

    def import_TrelloActivity(self, feed, course_code):
        #User needs to sign up username and board (board can be left out but is needed)
        #TODO: RP
        print 'Beginning trello import!'

        for action in list(feed):
            #print 'action: %s' % (action)
            #action = json.load(action)

            #We need to connect this with our user profile somewhere when they initially auth
            u_id = action['idMemberCreator']
            author = action['memberCreator']['username']
            type = action['type'] #commentCard, updateCard, createList,etc
            data = action['data']
            date = action['date']
            board_name = data['board']['name']

            print 'got action type: %s' % (type)

            #print 'is action comment? %s' % (type == 'commentCard')
            #Get all 'commented' verb actions
            if (type == self.ACTION_TYPE_COMMENT_CARD):
                #do stuff
                target_obj_id = data['card']['id']
                #date
                comment_from_uid = u_id
                comment_from_name = author
                comment_message = data['text']
                comment_id = action['id']
                card_name = data['card']['name']
                
                if username_exists(comment_from_uid, course_code, self.platform):
                    # Create "other" contextActivity object to store original activity in xAPI
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                    context = get_other_contextActivity(
                        card_details['shortUrl'], 'Verb', type, 
                        CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED))
                    other_context_list = [context]
                    usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)

                    insert_comment(usr_dict, target_obj_id, comment_id,
                                   comment_message, comment_from_uid,
                                   comment_from_name, date, course_code,
                                   self.platform, self.platform_url,
                                   shared_username = target_obj_id, shared_displayname = card_name,
                                   other_contexts = other_context_list)

                    print 'Inserted comment!'

            #print 'is action card creation? %s' % (type == 'createCard')
            #Get all 'create' verb actions
            if (type == self.ACTION_TYPE_CREATE_CARD): #, 'createList']):
                #date
                #list_id = data['list']['id']
                # task_id = data['card']['id']
                task_id = action['id']
                task_name = data['card']['name']

                if username_exists(u_id, course_code, self.platform):
                    # Create "other" contextActivity object to store original activity in xAPI
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                    context = get_other_contextActivity(
                        card_details['shortUrl'], 'Verb', type, 
                        CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED))
                    other_context_list = [context]
                    usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)

                    insert_task(usr_dict, task_id, task_name, u_id, author, date,
                                course_code, self.platform, self.platform_url, other_contexts = other_context_list) #, list_id=list_id)

                    #TODO: RP
                    print 'Inserted created card!'

            #Get all 'add' verbs (you tecnically aren't *creating* an attachment on
            #a card so....)
            #print 'is action an add event? %s' % (type in
            #    ['addAttachmentToCard', 'addMemberToBoard',
            #     'emailCard', 'addChecklistToCard'
            #     , 'addMemberToCard'])
            if (type in
                [self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD, 
                'addMemberToBoard', 'emailCard', 
                self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD, 
                self.ACTION_TYPE_ADD_MEMBER_TO_CARD]):

                # Get user details from Util class
                usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)

                other_context_list = []
                # TODO: Add emailCard and addMemberToBoard? Currently they aren't imported
                if type in [self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD, 
                            self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD, 
                            self.ACTION_TYPE_ADD_MEMBER_TO_CARD]:
                    # Create "other" contextActivity object to store original activity in xAPI
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                    context = get_other_contextActivity(
                        card_details['shortUrl'], 'Verb', type, 
                        CLRecipe.get_verb_iri(CLRecipe.VERB_ADDED))
                    other_context_list = [context]

                if type == self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD and usr_dict is not None:

                    target_id = data['card']['id']
                    attachment = data['attachment']
                    # attachment_id = attachment['id']
                    object_id = action['id']
                    attachment_data = '%s - %s' % (attachment['name'], attachment['url'])
                    object_type = CLRecipe.OBJECT_FILE
                    shared_displayname = '%sc/%s' % (self.platform_url, target_id)

                    insert_added_object(usr_dict, target_id, attachment_id, attachment_data,
                                        u_id, author, date, course_code, self.platform, self.platform_url,
                                        object_type, shared_displayname=shared_displayname,
                                        other_contexts = other_context_list)

                    #TODO: RP
                    print 'Added attachment!'

                if type == self.ACTION_TYPE_ADD_MEMBER_TO_CARD and usr_dict is not None: #or 'addMemberToBoard':

                    target_id = data['card']['id']
                    # object_id = data['idMember']
                    object_id = action['id']
                    object_data = action['member']['username']
                    object_type = CLRecipe.OBJECT_PERSON
                    shared_displayname = '%sc/%s' % (self.platform_url, target_id)

                    insert_added_object(usr_dict, target_id, object_id, object_data, u_id, author, date,
                                        course_code, self.platform, self.platform_url, object_type,
                                        shared_displayname=shared_displayname,
                                        other_contexts = other_context_list)

                    #TODO: RP
                    print 'Added add member to card!'

                if type == self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD and usr_dict is not None:

                    target_id = data['card']['id']
                    # object_id = data['idMember']
                    object_id = action['id']
                    object_data = None
                    checklist_items = None
                    object_type = CLRecipe.OBJECT_COLLECTION
                    shared_displayname = '%sc/%s' % (self.platform_url, target_id)

                    #get checklist contents
                    try:
                        checklist = self.TrelloCient.fetch_json('/checklists/' + data['checklist']['id'],)
                        checklist_items = checklist['checkItems']
                    except Exception:
                        print 'Could not retrieve checklist..'

                    #data will be a comma separated list of checklist-item ids (e.g.: 'id1,id2,id3...')
                    object_data = ','.join([item['id'] for item in checklist_items])

                    insert_added_object(usr_dict, target_id, object_id, object_data, u_id, author, date,
                                        course_code, self.platform, self.platform_url, object_type,
                                        shared_displayname=shared_displayname,
                                        other_contexts = other_context_list)

                    #TODO: RP
                    print 'added add checklist to card!'

            #print 'is action type an update? %s' % (type in
            #    ['updateCheckItemStateOnCard', 'updateBoard',
            #     'updateCard', 'updateCheckList',
            #     'updateList', 'updateMember'])
            #Get all 'updated' verbs
            if (type in
                [self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD, 'updateBoard',
                 self.ACTION_TYPE_UPDATE_CARD, 'updateCheckList',
                 'updateList', 'updateMember']):

                usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)
                #many checklist items will be bugged - we require webhooks!

                if type == self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD and usr_dict is not None:
                    # Create "other" contextActivity object to store original activity in xAPI
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                    context = get_other_contextActivity(
                        card_details['shortUrl'], 'Verb', type, 
                        CLRecipe.get_verb_iri(CLRecipe.VERB_UPDATED))
                    other_context_list = [context]

                    insert_updated_object(usr_dict,
                                          data['checkItem']['id'],
                                          data['checkItem']['state'],
                                          u_id, author, date, course_code,
                                          self.platform, self.platform_url,
                                          'checklist-item', obj_parent=data['checklist']['id'],
                                          obj_parent_type='checklist',
                                          other_contexts = other_context_list)
                    #TODO: RP
                    print 'add update checklist!'


                #type will only show 'updateCard'
                #up to us to figure out what's being updated
                if type == self.ACTION_TYPE_UPDATE_CARD:

                    #Get and store the values that were changed, usually it's only one
                    #TODO: Handle support for multiple changes, if that's possible
                    try:
                        change = [changed_value for changed_value in data['old']]
                    except Exception:
                       print 'Error occurred getting changes...'
                    #assert len(change) is 1

                    #TODO: Remove Print
                    print 'got changes: %s' % (change)

                    #Insert all updates that aren't closed
                    if change[0] == 'pos':
                        if 'listBefore' in data:
                            object_text = 'Move card from %s to %s' % (data['listBefore']['name'], data['listAfter']['name'])
                        else:
                            object_text = 'Move card from %s to %s' % (data['old']['pos'], data['card']['pos'])

                        context = get_other_contextActivity(
                            card_details['shortUrl'], 'Verb', self.ACTION_TYPE_MOVE_CARD, 
                            CLRecipe.get_verb_iri(CLRecipe.VERB_UPDATED))
                        other_context_list = [context]

                        insert_updated_object(usr_dict, action['id'],
                                              object_text, u_id, author, date, course_code,
                                              self.platform, self.platform_url,
                                              CLRecipe.OBJECT_TASK, obj_parent=data['list']['name'],
                                              obj_parent_type = CLRecipe.OBJECT_COLLECTION,
                                              other_contexts = other_context_list)

                        #TODO: RP
                        print 'added closed card!'
                    #add in close/open verbs
                    else:
                        if data['old'][change[0]] is False or data['old'][change[0]] is True:
                            verb_iri = CLRecipe.get_verb_iri(CLRecipe.VERB_CLOSED)
                            verb = CLRecipe.VERB_CLOSED
                            action_type = self.ACTION_TYPE_CLOSE_CARD
                            object_text = '%s:%s' % (CLRecipe.VERB_CLOSED, data['card']['name'])

                            if data['old'][change[0]] is True:
                                verb_iri = CLRecipe.get_verb_iri(CLRecipe.VERB_OPENED)
                                verb = CLRecipe.VERB_OPENED
                                action_type = self.ACTION_TYPE_OPEN_CARD
                                object_text = '%s:%s' % (CLRecipe.VERB_OPENED, data['card']['name'])

                            context = get_other_contextActivity(card_details['shortUrl'], 'Verb', action_type, verb_iri)
                            other_context_list = [context]

                            insert_closedopen_object(usr_dict, action['id'],
                                                 object_text, u_id, author, date, course_code,
                                                 self.platform, self.platform_url,
                                                 CLRecipe.OBJECT_TASK, verb, obj_parent = data['list']['name'],
                                                 obj_parent_type = CLRecipe.OBJECT_COLLECTION,
                                                 other_contexts = other_context_list)
                            #TODO: RP
                            print 'added closed/opened card!'

    def get_verbs(self):
        return self.xapi_verbs
            
    def get_objects(self):
        return self.xapi_objects

registry.register(TrelloPlugin)
