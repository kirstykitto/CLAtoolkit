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
from common.ClaUserUtil import ClaUserUtil
from common.CLRecipe import CLRecipe


class TrelloPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "Trello"
    platform_url = "http://www.trello.com/"

    #created for "create" actions
    #added for "add" actions
    #updated for "update" actions
    #commented for card "comment" actions
    # xapi_verbs = ['created', 'added', 'updated', 'commented', 'closed', 'opened']
    xapi_verbs = [CLRecipe.VERB_CREATED, CLRecipe.VERB_ADDED, CLRecipe.VERB_UPDATED, 
                CLRecipe.VERB_COMMENTED, CLRecipe.VERB_CLOSED, CLRecipe.VERB_OPENED]

    #Note for "commented" actions
    #Task for "created", "added", "updated", and "commented" actions
    #Collection for any "created", "added", "updated" List actions (tentative use)
    # xapi_objects = ['Note', 'Task', 'Collection', 'Person', 'File', 'checklist-item', 'checklist']
    xapi_objects = [CLRecipe.OBJECT_NOTE, CLRecipe.OBJECT_TASK, CLRecipe.OBJECT_COLLECTION, 
                    CLRecipe.OBJECT_PERSON, CLRecipe.OBJECT_FILE, CLRecipe.OBJECT_CHECKLIST_ITEM, CLRecipe.OBJECT_CHECKLIST]

    user_api_association_name = 'Trello UID' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Board ID' # eg hashtags or a group name

    config_json_keys = ['consumer_key', 'consumer_secret']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = [CLRecipe.OBJECT_NOTE]
    xapi_verbs_to_includein_verbactivitywidget = [CLRecipe.VERB_CREATED, CLRecipe.VERB_SHARED, 
                                                CLRecipe.VERB_LIKED, CLRecipe.VERB_COMMENTED]

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

    VERB_ACTION_TYPE_MAPPER = {
        CLRecipe.VERB_CREATED: [ACTION_TYPE_CREATE_CARD],
        CLRecipe.VERB_ADDED: [ACTION_TYPE_ADD_ATTACHMENT_TO_CARD, ACTION_TYPE_ADD_CHECKLIST_TO_CARD, ACTION_TYPE_ADD_MEMBER_TO_CARD],
        CLRecipe.VERB_UPDATED: [ACTION_TYPE_MOVE_CARD, ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD],
        CLRecipe.VERB_COMMENTED: [ACTION_TYPE_COMMENT_CARD],
        CLRecipe.VERB_CLOSED: [ACTION_TYPE_CLOSE_CARD],
        CLRecipe.VERB_OPENED: [ACTION_TYPE_OPEN_CARD]
    }

    SEPARATOR_COLON = ": "
    SEPARATOR_HTML_TAG_BR = "<br>"

    def __init__(self):
       pass

    #retreival param is the user_id
    def perform_import(self, retreival_param, course_code, token=None):
        #from clatoolkit.models import ApiCredentials
        #Set up trello auth and API
        self.TrelloCient = TrelloClient(
            api_key=os.environ.get("TRELLO_API_KEY"),
            token=token
        )

        #Get user-registered board in trello
        trello_board = self.TrelloCient.get_board(retreival_param)

        #Get boards activity/action feed
        trello_board.fetch_actions('all') #fetch_actions() collects actions feed and stores to trello_board.actions
        self.import_TrelloActivity(trello_board.actions, course_code)

    def import_TrelloActivity(self, feed, course_code):
        #User needs to sign up username and board (board can be left out but is needed)
        #TODO: RP
        print 'Beginning trello import!'

        for action in list(feed):
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
                
                if username_exists(comment_from_uid, course_code, self.platform.lower()):
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
                                   shared_username = card_name, shared_displayname = card_name,
                                   other_contexts = other_context_list)

                    # print 'Inserted comment!'

            #print 'is action card creation? %s' % (type == 'createCard')
            #Get all 'create' verb actions
            if (type == self.ACTION_TYPE_CREATE_CARD):
                action_id = action['id']
                card_name = data['card']['name']

                if username_exists(u_id, course_code, self.platform.lower()):
                    # Create "other" contextActivity object to store original activity in xAPI
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                    context = get_other_contextActivity(
                        card_details['shortUrl'], 'Verb', type, 
                        CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED))
                    other_context_list = [context]
                    usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)

                    insert_task(usr_dict, action_id, card_name, u_id, author, date,
                                course_code, self.platform, self.platform_url, other_contexts = other_context_list)

                    #TODO: RP
                    # print 'Inserted created card!'

            #Get all 'add' verbs (you tecnically aren't *creating* an attachment on
            #a card so....)
            #print 'is action an add event? %s' % (type in
            #    ['addAttachmentToCard', 'addMemberToBoard',
            #     'emailCard', 'addChecklistToCard'
            #     , 'addMemberToCard'])
            if (type in [self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD, 
                        self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD, 
                        self.ACTION_TYPE_ADD_MEMBER_TO_CARD]):

                # Get user details from Util class
                usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)
                other_context_list = []
                # Create "other" contextActivity object to store original activity in xAPI
                card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                context = get_other_contextActivity(
                    card_details['shortUrl'], 'Verb', type, 
                    CLRecipe.get_verb_iri(CLRecipe.VERB_ADDED))
                other_context_list = [context]

                if type == self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD and usr_dict is not None:

                    target_id = data['card']['id']
                    attachment = data['attachment']
                    attachment_id = action['id']
                    attachment_data = attachment['name'] + self.SEPARATOR_HTML_TAG_BR + attachment['url']
                    object_type = CLRecipe.OBJECT_FILE
                    shared_displayname = '%sc/%s' % (self.platform_url, target_id)

                    insert_added_object(usr_dict, target_id, attachment_id, attachment_data,
                                        u_id, author, date, course_code, self.platform, self.platform_url,
                                        object_type, shared_displayname=shared_displayname,
                                        other_contexts = other_context_list)

                    #TODO: RP
                    # print 'Added attachment!'

                if type == self.ACTION_TYPE_ADD_MEMBER_TO_CARD and usr_dict is not None: #or 'addMemberToBoard':

                    target_id = data['card']['id']
                    object_id = action['id']
                    object_data = action['member']['username']
                    object_type = CLRecipe.OBJECT_PERSON
                    shared_displayname = '%sc/%s' % (self.platform_url, target_id)

                    insert_added_object(usr_dict, target_id, object_id, object_data, u_id, author, date,
                                        course_code, self.platform, self.platform_url, object_type,
                                        shared_displayname = shared_displayname,
                                        other_contexts = other_context_list)

                    #TODO: RP
                    # print 'Added add member to card!'

                if type == self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD and usr_dict is not None:

                    target_id = data['card']['id']
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
                    object_data = 'Checklist: ' + data['checklist']['name'] + self.SEPARATOR_HTML_TAG_BR
                    object_data = object_data + self.SEPARATOR_HTML_TAG_BR.join([item['name'] for item in checklist_items])
                    insert_added_object(usr_dict, target_id, object_id, object_data, u_id, author, date,
                                        course_code, self.platform, self.platform_url, object_type,
                                        shared_displayname=shared_displayname,
                                        other_contexts = other_context_list)

                    #TODO: RP
                    # print 'added add checklist to card!'

            #print 'is action type an update? %s' % (type in
            #    ['updateCheckItemStateOnCard', 'updateBoard',
            #     'updateCard', 'updateCheckList',
            #     'updateList', 'updateMember'])
            #Get all 'updated' verbs
            if (type in [self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD, self.ACTION_TYPE_UPDATE_CARD]):
                usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)
                card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                #many checklist items will be bugged - we require webhooks!

                if type == self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD and usr_dict is not None:
                    # Create "other" contextActivity object to store original activity in xAPI
                    context = get_other_contextActivity(
                        card_details['shortUrl'], 'Verb', type, 
                        CLRecipe.get_verb_iri(CLRecipe.VERB_UPDATED))
                    other_context_list = [context]
                    # Import check item ID & its state
                    obj_val = data['checkItem']['name'] + self.SEPARATOR_COLON + data['checkItem']['state']

                    insert_updated_object(usr_dict, action['id'], obj_val,
                                          u_id, author, date, course_code,
                                          self.platform, self.platform_url,
                                          CLRecipe.OBJECT_CHECKLIST_ITEM, 
                                          obj_parent = data['checklist']['id'],
                                          obj_parent_type = CLRecipe.OBJECT_CHECKLIST,
                                          other_contexts = other_context_list)
                    #TODO: RP
                    # print 'add update checklist!'


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

                    if change[0] == 'pos':
                        # When user moves card in the same list (change order)
                        card_name = 'Card: ' + data['card']['name'] + self.SEPARATOR_HTML_TAG_BR
                        object_text = 'Change order of card: %s to %s' % (data['old']['pos'], data['card']['pos'])
                        object_text = card_name + object_text

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
                        # print 'added closed card!'
                    else:
                        # When user moves card from a list to another
                        if data.has_key('listBefore'):
                            card_name = 'Card: ' + data['card']['name'] + self.SEPARATOR_HTML_TAG_BR
                            object_text = 'from %s to %s' % (data['listBefore']['name'], data['listAfter']['name'])
                            object_text = card_name + object_text

                            context = get_other_contextActivity(
                                card_details['shortUrl'], 'Verb', self.ACTION_TYPE_MOVE_CARD, 
                                CLRecipe.get_verb_iri(CLRecipe.VERB_UPDATED))
                            other_context_list = [context]

                            insert_updated_object(usr_dict, action['id'],
                                                  object_text, u_id, author, date, course_code,
                                                  self.platform, self.platform_url,
                                                  CLRecipe.OBJECT_TASK, obj_parent=data['card']['id'],
                                                  obj_parent_type = CLRecipe.OBJECT_COLLECTION,
                                                  other_contexts = other_context_list)

                        # When user closes (archives)/opens card
                        elif data['old'][change[0]] is False or data['old'][change[0]] is True:
                            verb = CLRecipe.VERB_CLOSED
                            verb_iri = CLRecipe.get_verb_iri(verb)
                            action_type = self.ACTION_TYPE_CLOSE_CARD
                            object_text = data['card']['name']

                            # When card is opened
                            if data['old'][change[0]] is True:
                                verb = CLRecipe.VERB_OPENED
                                verb_iri = CLRecipe.get_verb_iri(verb)
                                action_type = self.ACTION_TYPE_OPEN_CARD

                            context = get_other_contextActivity(card_details['shortUrl'], 'Verb', action_type, verb_iri)
                            other_context_list = [context]
                            insert_closedopen_object(usr_dict, action['id'],
                                                 object_text, u_id, author, date, course_code,
                                                 self.platform, self.platform_url,
                                                 CLRecipe.OBJECT_TASK, verb, obj_parent = data['list']['name'],
                                                 obj_parent_type = CLRecipe.OBJECT_COLLECTION,
                                                 other_contexts = other_context_list)
                            #TODO: RP
                            # print 'added closed/opened card!'

    def get_verbs(self):
        return self.xapi_verbs
            
    def get_objects(self):
        return self.xapi_objects

    def get_other_contextActivity_types(self, verbs = []):
        ret = []
        if verbs is None or len(verbs) == 0:
            ret = [self.ACTION_TYPE_COMMENT_CARD, self.ACTION_TYPE_CREATE_CARD, 
                self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD, self.ACTION_TYPE_UPDATE_CARD, 
                self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD, self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD, 
                self.ACTION_TYPE_ADD_MEMBER_TO_CARD, self.ACTION_TYPE_MOVE_CARD, 
                self.ACTION_TYPE_CLOSE_CARD, self.ACTION_TYPE_OPEN_CARD]
        else:
            for verb in verbs:
                action_types = self.VERB_ACTION_TYPE_MAPPER[verb]
                for type in action_types:
                    ret.append(type)
        return ret


    def getActionTypeDisplayNames(self, mapper):
        if mapper is None:
            return mapper

        ret = {}
        for key, val in mapper.iteritems():
            for action in mapper[key]:
                ret[action] = self.getActionTypeDisplayName(action)

        return ret


    def getActionTypeDisplayName(self, action):
        if action == self.ACTION_TYPE_CREATE_CARD:
            return 'Created card'
        elif action == self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD:
            return 'Added attachment to card'
        elif action == self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD:
            return 'Added checklist to card'
        elif action == self.ACTION_TYPE_ADD_MEMBER_TO_CARD:
            return 'Added member to card'
        elif action == self.ACTION_TYPE_MOVE_CARD:
            return 'Moved card'
        elif action == self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD:
            return 'Updated checklist item state'
        elif action == self.ACTION_TYPE_COMMENT_CARD:
            return 'Commented on card'
        elif action == self.ACTION_TYPE_CLOSE_CARD:
            return 'Closed card'
        elif action == self.ACTION_TYPE_OPEN_CARD:
            return 'Opened card'
        else:
            return 'Unknown action type'


    # def convertValues(self, data):
    #     for data in data:
    #         for series in data['series']:
    #             for val in series['values']:
    #                 if series["name"] == self.ACTION_TYPE_ADD_MEMBER_TO_CARD:
    #                     pass
    #                 elif series["name"] == self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD:
    #                     pass
    #                 elif series["name"] == self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD:
    #                     # convert item id to item name (and list id to list name?)
    #                     items = val.split(self.SEPARATOR_COLON)
    #                     checklist_id = items[0]
    #                     items = []
    #                     index = 1
    #                     for items in range(1, len(items)):
    #                         items.append(items[index])
    #                         index = index + 1
    #                     item_names = self.get_trello_checkitems(checklist_id, items)

    #                     alldata = 'Checklist: ' + checklist_id + self.SEPARATOR_HTML_TAG_BR
    #                     alldata = alldata + self.SEPARATOR_HTML_TAG_BR.join(item_names)

    #                     print alldata

    #                     val = alldata

    #                 elif series["name"] == self.ACTION_TYPE_CREATE_CARD:
    #                     # convert card id to name
    #                     pass
    #                 elif series["name"] == self.ACTION_TYPE_OPEN_CARD:
    #                     # convert card id to name
    #                     pass
    #                 elif series["name"] == self.ACTION_TYPE_CLOSE_CARD:
    #                     # convert card id to name
    #                     pass
    #                 elif series["name"] == self.ACTION_TYPE_MOVE_CARD:
    #                     # convert card id to name (move to and from)
    #                     pass
    #                 elif series["name"] == self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD:
    #                     # convert chckelist item id to name
    #                     pass

    #     return data

    # def get_trello_checkitems(self, checklist_id, item_ids):
    #     self.TrelloCient = TrelloClient(
    #         api_key=os.environ.get("TRELLO_API_KEY")
    #         # token=token
    #     )
    #     checklist = self.TrelloCient.fetch_json('/checklists/' + checklist_id,)
    #     item_names = []
    #     for item_id in item_ids:
    #         for item in checklist['checkItems']:
    #             if item_id == item['id']:
    #                 item_names.append(item['name'])
    #             else:
    #                 item_names.append(item_id)

    #     return item_names




registry.register(TrelloPlugin)
