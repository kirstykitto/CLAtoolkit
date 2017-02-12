__author__ = 'zak'

from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin, DIAuthomaticPluginMixin
from dataintegration.core.importer import *
from dataintegration.core.di_utils import * #Formerly dataintegration.core.recipepermissions
from xapi.statement.builder import * #Formerly dataintegration.core.socialmediabuilder
from xapi.statement.xapi_settings import xapi_settings
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
<<<<<<< HEAD
from common.CLRecipe import CLRecipe
=======
>>>>>>> upstream_master


class TrelloPlugin(DIBasePlugin, DIPluginDashboardMixin):

<<<<<<< HEAD
    platform = "Trello"
    platform_url = "http://www.trello.com/"
=======
    platform = xapi_settings.PLATFORM_TRELLO
    platform_url = "https://trello.com"
>>>>>>> upstream_master

    #created for "create" actions
    #added for "add" actions
    #updated for "update" actions
    #commented for card "comment" actions
    # xapi_verbs = ['created', 'added', 'updated', 'commented', 'closed', 'opened']
<<<<<<< HEAD
    xapi_verbs = [CLRecipe.VERB_CREATED, CLRecipe.VERB_ADDED, CLRecipe.VERB_UPDATED, 
                CLRecipe.VERB_COMMENTED, CLRecipe.VERB_CLOSED, CLRecipe.VERB_OPENED]
=======
    xapi_verbs = [xapi_settings.VERB_CREATED, xapi_settings.VERB_ADDED, xapi_settings.VERB_UPDATED, 
                xapi_settings.VERB_COMMENTED, xapi_settings.VERB_CLOSED, xapi_settings.VERB_OPENED]
>>>>>>> upstream_master

    #Note for "commented" actions
    #Task for "created", "added", "updated", and "commented" actions
    #Collection for any "created", "added", "updated" List actions (tentative use)
    # xapi_objects = ['Note', 'Task', 'Collection', 'Person', 'File', 'checklist-item', 'checklist']
<<<<<<< HEAD
    xapi_objects = [CLRecipe.OBJECT_NOTE, CLRecipe.OBJECT_TASK, CLRecipe.OBJECT_COLLECTION, 
                    CLRecipe.OBJECT_PERSON, CLRecipe.OBJECT_FILE, CLRecipe.OBJECT_CHECKLIST_ITEM, CLRecipe.OBJECT_CHECKLIST]
=======
    xapi_objects = [xapi_settings.OBJECT_NOTE, xapi_settings.OBJECT_TASK, xapi_settings.OBJECT_COLLECTION, 
                    xapi_settings.OBJECT_PERSON, xapi_settings.OBJECT_FILE, xapi_settings.OBJECT_CHECKLIST_ITEM, xapi_settings.OBJECT_CHECKLIST]
>>>>>>> upstream_master

    user_api_association_name = 'Trello UID' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Board ID' # eg hashtags or a group name

    config_json_keys = ['consumer_key', 'consumer_secret']

    #from DIPluginDashboardMixin
<<<<<<< HEAD
    xapi_objects_to_includein_platformactivitywidget = [CLRecipe.OBJECT_NOTE]
    xapi_verbs_to_includein_verbactivitywidget = [CLRecipe.VERB_CREATED, CLRecipe.VERB_SHARED, 
                                                CLRecipe.VERB_LIKED, CLRecipe.VERB_COMMENTED]
=======
    xapi_objects_to_includein_platformactivitywidget = [xapi_settings.OBJECT_NOTE]
    xapi_verbs_to_includein_verbactivitywidget = [xapi_settings.VERB_CREATED, xapi_settings.VERB_SHARED, 
                                                xapi_settings.VERB_LIKED, xapi_settings.VERB_COMMENTED]
>>>>>>> upstream_master

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

    VERB_OBJECT_MAPPER = {
<<<<<<< HEAD
        CLRecipe.VERB_CREATED: [ACTION_TYPE_CREATE_CARD],
        CLRecipe.VERB_ADDED: [ACTION_TYPE_ADD_ATTACHMENT_TO_CARD, ACTION_TYPE_ADD_CHECKLIST_TO_CARD, ACTION_TYPE_ADD_MEMBER_TO_CARD],
        CLRecipe.VERB_UPDATED: [ACTION_TYPE_MOVE_CARD, ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD],
        CLRecipe.VERB_COMMENTED: [ACTION_TYPE_COMMENT_CARD],
        CLRecipe.VERB_CLOSED: [ACTION_TYPE_CLOSE_CARD],
        CLRecipe.VERB_OPENED: [ACTION_TYPE_OPEN_CARD]
=======
        xapi_settings.VERB_CREATED: [ACTION_TYPE_CREATE_CARD],
        xapi_settings.VERB_ADDED: [ACTION_TYPE_ADD_ATTACHMENT_TO_CARD, ACTION_TYPE_ADD_CHECKLIST_TO_CARD, ACTION_TYPE_ADD_MEMBER_TO_CARD],
        xapi_settings.VERB_UPDATED: [ACTION_TYPE_MOVE_CARD, ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD],
        xapi_settings.VERB_COMMENTED: [ACTION_TYPE_COMMENT_CARD],
        xapi_settings.VERB_CLOSED: [ACTION_TYPE_CLOSE_CARD],
        xapi_settings.VERB_OPENED: [ACTION_TYPE_OPEN_CARD]
>>>>>>> upstream_master
    }

    SEPARATOR_COLON = ": "
    SEPARATOR_HTML_TAG_BR = "<br>"
    MESSAGE_CARD_POSITION_CHANGED = 'Card position was changed.'

    def __init__(self):
       pass

    #retreival param is the user_id
    def perform_import(self, retreival_param, unit, token=None):
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
<<<<<<< HEAD
        self.import_TrelloActivity(trello_board.actions, course_code)
=======
        self.import_TrelloActivity(trello_board.actions, unit)

>>>>>>> upstream_master

    def import_TrelloActivity(self, feed, unit):
        #User needs to sign up username and board (board can be left out but is needed)
<<<<<<< HEAD
        #TODO: RP
        print 'Beginning trello import!'
=======
        print 'Beginning Trello import!'
>>>>>>> upstream_master

        for action in list(feed):
            #We need to connect this with our user profile somewhere when they initially auth
            u_id = action['idMemberCreator']
            author = action['memberCreator']['username']
            type = action['type'] #commentCard, updateCard, createList,etc
            data = action['data']
            date = action['date']
            board_name = data['board']['name']

            # print 'got action type: %s' % (type)

            #Get all 'commented' verb actions
            if (type == self.ACTION_TYPE_COMMENT_CARD):
<<<<<<< HEAD
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
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id'])
                    usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)
                    insert_comment(usr_dict, target_obj_id, comment_id,
                                   comment_message, comment_from_uid,
                                   comment_from_name, date, course_code,
                                   self.platform, self.platform_url,
                                   shared_username = card_name, shared_displayname = card_name,
                                   parent_name = data['card']['name'])

                    # print 'Inserted comment!'

            #print 'is action card creation? %s' % (type == 'createCard')
            #Get all 'create' verb actions
            if (type == self.ACTION_TYPE_CREATE_CARD):
                action_id = action['id']
                card_name = data['card']['name']

                if username_exists(u_id, course_code, self.platform.lower()):
                    # Create "other" contextActivity object to store original activity in xAPI
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id'])
                    usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)

                    insert_task(usr_dict, action_id, card_name, u_id, author, date,
                                course_code, self.platform, self.platform_url, 
                                parent_id = data['list']['id'], parent_name = data['list']['name'], 
                                parent_object_type = CLRecipe.OBJECT_COLLECTION)

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
                
                # Create "other" contextActivity object to store original activity in xAPI
                other_context_list = []
                card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id'])

                if type == self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD and usr_dict is not None:

                    target_id = data['card']['id']
                    attachment = data['attachment']
                    attachment_id = action['id']
                    attachment_data = attachment['name']
                    object_type = CLRecipe.OBJECT_FILE
                    shared_displayname = '%sc/%s' % (self.platform_url, target_id)
                    
                    # Extensions
                    extensions = get_file_extensions(url = attachment['url'])
                    insert_added_object(usr_dict, target_id, attachment_id, attachment_data,
                                        u_id, author, date, course_code, self.platform, self.platform_url,
                                        object_type, shared_displayname=shared_displayname,
                                        parent_name = data['card']['name'], extensions = extensions)

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
                                        shared_displayname = shared_displayname, parent_name = data['card']['name'])

                    # Put the card name in other context

                    #TODO: RP
                    # print 'Added add member to card!'

                if type == self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD and usr_dict is not None:

                    target_id = data['card']['id']
                    object_id = action['id']
                    object_data = None
                    checklist_items = None
                    object_type = CLRecipe.OBJECT_COLLECTION
                    shared_displayname = '%sc/%s' % (self.platform_url, target_id)
=======
                target_obj_id = self.create_card_url(data)
                comment_from_uid = u_id
                comment_from_name = author
                comment_message = data['text']
                comment_id = target_obj_id + '/' + action['id']
                card_name = data['card']['name']
                
                if username_exists(comment_from_uid, unit, self.platform):
                    # Create "other" contextActivity object to store original activity in xAPI
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                    context = get_other_contextActivity(
                        card_details['shortUrl'], 'Verb', type, 
                        xapi_settings.get_verb_iri(xapi_settings.VERB_COMMENTED))
                    context2 = get_other_contextActivity(
                        card_details['shortUrl'], 'Object', data['card']['name'], 
                        xapi_settings.get_verb_iri(xapi_settings.VERB_COMMENTED))
                    other_context_list = [context, context2]

                    user = get_user_from_screen_name(comment_from_uid, self.platform)
                    insert_comment(user, target_obj_id, comment_id, comment_message, date, unit, 
                                   self.platform, self.platform_url, parent_user_external = card_name, 
                                   other_contexts = other_context_list)


            if (type == self.ACTION_TYPE_CREATE_CARD):
                object_id = self.create_card_url(data) + '/' + action['id']
                card_name = data['card']['name']
                parent_id = self.create_list_url(data)
                
                if username_exists(u_id, unit, self.platform):
                    # Create "other" contextActivity object to store original activity in xAPI
                    card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                    context = get_other_contextActivity(
                        card_details['shortUrl'], 'Verb', type, 
                        xapi_settings.get_verb_iri(xapi_settings.VERB_CREATED))
                    context2 = get_other_contextActivity(
                        card_details['shortUrl'], 'Object', data['list']['name'], 
                        xapi_settings.get_verb_iri(xapi_settings.VERB_CREATED))
                    other_context_list = [context, context2]
                    usr_dict = ClaUserUtil.get_user_details_by_smid(u_id, self.platform)
                    user = get_user_from_screen_name(u_id, self.platform)

                    insert_task(user, object_id, card_name, date, unit, self.platform, self.platform_url, 
                        parent_id = parent_id, other_contexts = other_context_list)


            #Get all 'add' verbs (you tecnically aren't *creating* an attachment on a card so....)
            if (type in [self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD, self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD, 
                        self.ACTION_TYPE_ADD_MEMBER_TO_CARD]):
                user = get_user_from_screen_name(u_id, self.platform)
                if user is None:
                    continue

                card_url = self.create_card_url(data)
                
                # Create "other" contextActivity object to store original activity in xAPI
                other_context_list = []
                card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                context = get_other_contextActivity(
                    card_details['shortUrl'], 'Verb', type, 
                    xapi_settings.get_verb_iri(xapi_settings.VERB_ADDED))
                other_context_list.append(context)
                context2 = get_other_contextActivity(
                    card_details['shortUrl'], 'Object', data['card']['name'], 
                    xapi_settings.get_verb_iri(xapi_settings.VERB_ADDED))
                other_context_list = [context, context2]

                if type == self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD:

                    attachment = data['attachment']
                    attachment_id = card_url + '/' + data['attachment']['id']
                    attachment_data = attachment['name']
                    object_type = xapi_settings.OBJECT_FILE
                    parent_user_external = '%sc/%s' % (self.platform_url, card_url)
                    other_context_list.append(get_other_contextActivity(
                        card_details['shortUrl'], 'Object', attachment['url'], 
                        xapi_settings.get_verb_iri(xapi_settings.VERB_ADDED)))

                    insert_added_object(user, card_url, attachment_id, attachment_data, date, unit, 
                                        self.platform, self.platform_url,object_type, 
                                        parent_user_external = parent_user_external,
                                        other_contexts = other_context_list)


                if type == self.ACTION_TYPE_ADD_MEMBER_TO_CARD: #or 'addMemberToBoard':
                    
                    object_id = card_url + '/' + action['member']['id']
                    object_data = action['member']['username']
                    object_type = xapi_settings.OBJECT_PERSON
                    parent_user_external = '%sc/%s' % (self.platform_url, card_url)

                    insert_added_object(user, card_url, object_id, object_data, date, unit, 
                                        self.platform, self.platform_url, object_type,
                                        parent_user_external = parent_user_external,
                                        other_contexts = other_context_list)


                if type == self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD:

                    object_id = card_url + '/' + data['checklist']['id']
                    object_data = None
                    checklist_items = None
                    object_type = xapi_settings.OBJECT_COLLECTION
                    parent_user_external = '%sc/%s' % (self.platform_url, card_url)
>>>>>>> upstream_master

                    #get checklist contents
                    try:
                        checklist = self.TrelloCient.fetch_json('/checklists/' + data['checklist']['id'],)
                        checklist_items = checklist['checkItems']
                    except Exception:
                        print 'Could not retrieve checklist..'
<<<<<<< HEAD

                    object_data = data['checklist']['name']
                    def_type = CLRecipe.get_object_iri(CLRecipe.OBJECT_CHECKLIST_ITEM)
                    ext_items = []
                    for item in checklist_items:
                        ext_items.append(get_object_extension_dict(
                            def_type = def_type, obj_id = item['id'], obj_name = item['name']))

                    # Extensions
                    extensions = get_collection_extensions(ext_items)
                    insert_added_object(usr_dict, target_id, object_id, object_data, u_id, author, date,
                                        course_code, self.platform, self.platform_url, object_type,
                                        shared_displayname=shared_displayname,
                                        parent_name = data['card']['name'], extensions = extensions)

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
                    # Import check item ID & its state
                    obj_val = data['checkItem']['state']
                    insert_updated_object(usr_dict, action['id'], obj_val,
                                          u_id, author, date, course_code,
                                          self.platform, self.platform_url,
                                          CLRecipe.OBJECT_CHECKLIST_ITEM, 
                                          obj_parent = data['checklist']['id'],
                                          obj_parent_type = CLRecipe.OBJECT_CHECKLIST,
                                          parent_name = data['checkItem']['name'])
                    #TODO: RP
                    # print 'add update checklist!'
=======
                        continue

                    object_data = data['checklist']['name']
                    for item in checklist_items:
                        # items are stored individually in other contextActivities
                        other_context_list.append(get_other_contextActivity(
                            card_details['shortUrl'], 'Object', item['name'], 
                            xapi_settings.get_verb_iri(xapi_settings.VERB_ADDED)))

                    insert_added_object(user, card_url, object_id, object_data, date, unit, 
                                        self.platform, self.platform_url, object_type,
                                        parent_user_external=parent_user_external,
                                        other_contexts = other_context_list)


            if (type in [self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD, self.ACTION_TYPE_UPDATE_CARD]):
                user = get_user_from_screen_name(u_id, self.platform)
                if user is None:
                    continue
                
                card_details = self.TrelloCient.fetch_json('/cards/' + data['card']['id']);
                #many checklist items will be bugged - we require webhooks!

                if type == self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD:
                    # Import check item ID & its state
                    # Use action ID as an object ID to avoid ID conflict. 
                    object_id = self.create_card_url(data) + '/' + action['id']
                    obj_val = data['checkItem']['state']
                    
                    # Create "other" contextActivity object to store original activity in xAPI
                    other_context_list = []
                    other_context_list.append(get_other_contextActivity(
                        self.create_checklist_url(data), 'Verb', type, 
                        xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))
                    other_context_list.append(get_other_contextActivity(
                        card_details['shortUrl'], 'Object', data['checkItem']['name'], 
                        xapi_settings.get_verb_iri(xapi_settings.OBJECT_CHECKLIST_ITEM)))
                    other_context_list.append(get_other_contextActivity(
                        card_details['shortUrl'], 'Object', data['card']['name'], 
                        xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))

                    insert_updated_object(user, object_id, obj_val, date, unit, self.platform, self.platform_url,
                                          xapi_settings.OBJECT_CHECKLIST_ITEM, parent_id = self.create_checklist_url(data),
                                          obj_parent_type = xapi_settings.OBJECT_CHECKLIST,
                                          other_contexts = other_context_list)

>>>>>>> upstream_master

                #up to us to figure out what's being updated
                if type == self.ACTION_TYPE_UPDATE_CARD:

                    #Get and store the values that were changed, usually it's only one
                    #TODO: Handle support for multiple changes, if that's possible
                    try:
                        change = [changed_value for changed_value in data['old']]
                    except Exception:
                       print 'Error occurred getting changes...'

<<<<<<< HEAD
                    #TODO: Remove Print
                    # print 'got changes: %s' % (change)
                    if change[0] == 'pos':
                        # When user moves card within the list (changed order)
                        object_text = data['card']['name']
                        # Extensions
                        extensions = get_move_extensions(
                            data['card']['id'], data['card']['name'], CLRecipe.OBJECT_TASK, 
                            data['card']['id'], data['card']['name'], CLRecipe.OBJECT_TASK, 
                            old_pos = str(data['old']['pos']), new_pos = str(data['card']['pos']))
                        insert_updated_object(usr_dict, action['id'],
                                              object_text, u_id, author, date, course_code,
                                              self.platform, self.platform_url,
                                              CLRecipe.OBJECT_TASK, obj_parent=data['list']['id'],
                                              obj_parent_type = CLRecipe.OBJECT_COLLECTION,
                                              parent_name = data['list']['name'], extensions = extensions)

                        #TODO: RP
                        # print 'added closed card!'
=======
                    # Use action ID as an object ID to avoid ID conflict. 
                    object_id = self.create_card_url(data) + '/' + action['id']

                    if change[0] == 'pos':
                        # When user moves card in the same list (change order)

                        object_text = data['card']['name']
                        # object_text = 'Change order of card: %s to %s' % (data['old']['pos'], data['card']['pos'])
                        # object_text = card_name + object_text
                        other_context_list = []
                        other_context_list.append(get_other_contextActivity(
                            card_details['shortUrl'], 'Verb', self.ACTION_TYPE_MOVE_CARD, 
                            xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))
                        other_context_list.append(get_other_contextActivity(
                            card_details['shortUrl'], 'Object', self.MESSAGE_CARD_POSITION_CHANGED,
                            xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))
                        other_context_list.append(get_other_contextActivity(
                            card_details['shortUrl'], 'Object', str(data['old']['pos']), 
                            xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))
                        other_context_list.append(get_other_contextActivity(
                            card_details['shortUrl'], 'Object', str(data['card']['pos']), 
                            xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))

                        insert_updated_object(user, object_id, object_text, date, unit, self.platform, self.platform_url,
                                              xapi_settings.OBJECT_TASK, parent_id = self.create_list_url(data),
                                              obj_parent_type = xapi_settings.OBJECT_COLLECTION,
                                              other_contexts = other_context_list)

>>>>>>> upstream_master
                    else:
                        # When user moves card from a list to another
                        if data.has_key('listBefore'):
                            object_text = data['card']['name']
<<<<<<< HEAD
                            # Extensions
                            extensions = get_move_extensions(
                                data['listBefore']['id'], 
                                data['listBefore']['name'], 
                                CLRecipe.OBJECT_COLLECTION, 
                                new_obj_id = data['listAfter']['id'], 
                                new_obj_name = data['listAfter']['name'], 
                                new_obj_type = CLRecipe.OBJECT_COLLECTION)

                            insert_updated_object(usr_dict, action['id'],
                                                  object_text, u_id, author, date, course_code,
                                                  self.platform, self.platform_url,
                                                  CLRecipe.OBJECT_TASK, obj_parent=data['listAfter']['id'],
                                                  obj_parent_type = CLRecipe.OBJECT_COLLECTION,
                                                  parent_name = data['listAfter']['name'], extensions = extensions)

                        # When user closes (archives)/opens card
                        elif data['old'][change[0]] is False or data['old'][change[0]] is True:
                            verb = CLRecipe.VERB_CLOSED
                            verb_iri = CLRecipe.get_verb_iri(verb)
=======
                            # object_text = 'from %s to %s' % (data['listBefore']['name'], data['listAfter']['name'])
                            # object_text = card_name + object_text
                            
                            other_context_list = []
                            other_context_list.append(get_other_contextActivity(
                                card_details['shortUrl'], 'Verb', self.ACTION_TYPE_MOVE_CARD,
                                xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))
                            other_context_list.append(get_other_contextActivity(
                                card_details['shortUrl'], 'Object', data['listBefore']['name'],
                                xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))
                            other_context_list.append(get_other_contextActivity(
                                card_details['shortUrl'], 'Object', data['listAfter']['name'],
                                xapi_settings.get_verb_iri(xapi_settings.VERB_UPDATED)))

                            insert_updated_object(user, object_id, object_text, date, unit, self.platform, self.platform_url,
                                                  xapi_settings.OBJECT_TASK, parent_id = self.create_card_url(data),
                                                  obj_parent_type = xapi_settings.OBJECT_COLLECTION,
                                                  other_contexts = other_context_list)

                        # When user closes (archives)/opens card
                        elif data['old'][change[0]] is False or data['old'][change[0]] is True:
                            verb = xapi_settings.VERB_CLOSED
                            verb_iri = xapi_settings.get_verb_iri(verb)
>>>>>>> upstream_master
                            action_type = self.ACTION_TYPE_CLOSE_CARD
                            object_text = data['card']['name']

                            # When card is opened
                            if data['old'][change[0]] is True:
<<<<<<< HEAD
                                verb = CLRecipe.VERB_OPENED
                                verb_iri = CLRecipe.get_verb_iri(verb)
                                action_type = self.ACTION_TYPE_OPEN_CARD

                            insert_closedopen_object(usr_dict, action['id'],
                                                 object_text, u_id, author, date, course_code,
                                                 self.platform, self.platform_url,
                                                 CLRecipe.OBJECT_TASK, verb, obj_parent = data['list']['id'],
                                                 obj_parent_type = CLRecipe.OBJECT_COLLECTION,
                                                 parent_name = data['list']['name'])
                            #TODO: RP
                            # print 'added closed/opened card!'
=======
                                verb = xapi_settings.VERB_OPENED
                                verb_iri = xapi_settings.get_verb_iri(verb)
                                action_type = self.ACTION_TYPE_OPEN_CARD

                            other_context_list = []
                            other_context_list.append(get_other_contextActivity(
                                card_details['shortUrl'], 'Verb', action_type, verb_iri))
                            other_context_list.append(get_other_contextActivity(
                                card_details['shortUrl'], 'Object', data['list']['name'], verb_iri))

                            insert_closedopen_object(user, object_id, object_text, date, unit, 
                                                 self.platform, self.platform_url,
                                                 xapi_settings.OBJECT_TASK, verb, parent_id = self.create_list_url(data),
                                                 obj_parent_type = xapi_settings.OBJECT_COLLECTION,
                                                 other_contexts = other_context_list)



    def create_card_url(self, data):
        return self.platform_url + '/c/' + str(data['card']['id'])

    def create_list_url(self, data):
        return self.platform_url + '/b/' + str(data['board']['id']) + '/' + str(data['list']['id'])

    def create_checklist_url(self, data):
        return self.platform_url + '/b/' + str(data['board']['id']) + '/' + str(data['checklist']['id'])
>>>>>>> upstream_master

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
                action_types = self.VERB_OBJECT_MAPPER[verb]
                for type in action_types:
                    ret.append(type)
        return ret


    def get_display_names(self, mapper):
        if mapper is None:
            return mapper

        ret = {}
        for key, val in mapper.iteritems():
            for action in mapper[key]:
                ret[action] = self.get_action_type_display_name(action)

        return ret


    def get_action_type_display_name(self, action):
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

<<<<<<< HEAD
    def get_detail_values_by_fetch_results(self, result):
        all_rows = []
        for row in result:
            single_row = []
            single_row.append(row[0]) # user name
            single_row.append(self.get_action_type_from_context(row[2])) # verb or Trello action type
            single_row.append(row[3]) # date
            single_row.append(self.get_object_values_from_context(row)) # object values
            all_rows.append(single_row)

        return all_rows
        
=======

    def get_detail_values_by_fetch_results(self, xapi_statements):
        all_rows = []
        # return all_rows
        for stmt in xapi_statements:
            single_row = []
            # user name
            name = ''
            if 'name' in stmt['authority']['member'][0]:
                name = stmt['authority']['member'][0]['name']
            else:
                name = stmt['authority']['member'][1]['name']

            single_row.append(name)
            # verb or original action type 
            other_context_activities = stmt['context']['contextActivities']['other']
            single_row.append(self.get_action_type_from_context(other_context_activities))
            # Date
            dt = Utility.convert_to_datetime_object(stmt['timestamp'])
            date_str = str(dt.year) + ',' + str(dt.month) + ',' + str(dt.day)
            # date_str += ' ' + str(dt.hour) + ':' + str(dt.minute) + ':' + str(dt.second)
            single_row.append(date_str)

            # Value of an object
            single_row.append(self.get_object_diaplay_value(stmt))
            all_rows.append(single_row)
        return all_rows
        

>>>>>>> upstream_master
    def get_action_type_from_context(self, json):
        return json[0]['definition']['name']['en-US']


<<<<<<< HEAD
    def get_object_values_from_context(self, row):
        action = self.get_action_type_from_context(row[2])
        if len(row[2]) <= 1:
            return row[4]

        object_val = row[4]
        contexts = row[2]
=======
    def get_object_diaplay_value(self, stmt):
        other_context_activities = stmt['context']['contextActivities']['other']
        action = self.get_action_type_from_context(other_context_activities)
        object_val = stmt['object']['definition']['name']['en-US']
        if len(other_context_activities) <= 1:
            return object_val

        object_val = object_val
        contexts = other_context_activities
>>>>>>> upstream_master
        value = ''
        index = 1
        if action == self.ACTION_TYPE_CREATE_CARD:
            value = "created %s in %s" % (self.italicize(object_val), self.italicize(contexts[index]['definition']['name']['en-US']))

        elif action == self.ACTION_TYPE_ADD_ATTACHMENT_TO_CARD:
            value = "attached %s to %s" % (self.italicize(object_val), self.italicize(contexts[index]['definition']['name']['en-US']))
            value = value + self.SEPARATOR_HTML_TAG_BR
            index = index + 1
            value = value + contexts[index]['definition']['name']['en-US']

        elif action == self.ACTION_TYPE_ADD_CHECKLIST_TO_CARD:
            value = "added %s to %s" % (self.italicize(object_val), self.italicize(contexts[index]['definition']['name']['en-US']))
            value = value + self.SEPARATOR_HTML_TAG_BR
            index = index + 1
            for key in range(index, len(contexts)):
                value = value + ' ' + contexts[key]['definition']['name']['en-US'] + self.SEPARATOR_HTML_TAG_BR

        elif action == self.ACTION_TYPE_ADD_MEMBER_TO_CARD:
            value = "added %s to %s" % (self.italicize(object_val), self.italicize(contexts[index]['definition']['name']['en-US']))
            value = value + self.SEPARATOR_HTML_TAG_BR

        elif action == self.ACTION_TYPE_MOVE_CARD:
            if contexts[index]['definition']['name']['en-US'] == self.MESSAGE_CARD_POSITION_CHANGED:
                value = contexts[index]['definition']['name']['en-US']
                value = value + self.SEPARATOR_HTML_TAG_BR
                value = value + self.italicize(object_val)
            else:
                value = "moved %s" % (self.italicize(object_val))
                value = value + " from %s" % (self.italicize(contexts[index]['definition']['name']['en-US']))
                index = index + 1
                value = value + " to %s" % (self.italicize(contexts[index]['definition']['name']['en-US']))
            
        elif action == self.ACTION_TYPE_UPDATE_CHECKITEM_STATE_ON_CARD:
            value = "%s: %s" % (self.italicize(contexts[index]['definition']['name']['en-US']), self.italicize(object_val))

        elif action == self.ACTION_TYPE_COMMENT_CARD:
            value = 'commented in %s' % self.italicize(contexts[index]['definition']['name']['en-US'])
            value = value + self.SEPARATOR_HTML_TAG_BR
            value = value + self.italicize(self.replace_linechange_with_br_tag(object_val))

        elif action == self.ACTION_TYPE_CLOSE_CARD:
            value = "closed %s in %s" % (self.italicize(object_val), self.italicize(contexts[index]['definition']['name']['en-US']))

        elif action == self.ACTION_TYPE_OPEN_CARD:
            value = "opened %s in %s" % (self.italicize(object_val), self.italicize(contexts[index]['definition']['name']['en-US']))

        else:
            value = self.italicize(object_val)

        return value


    def italicize(self, value):
        return '<i>%s</i>' % (value)

    def replace_linechange_with_br_tag(self, target):
        return target.replace('\n','<br>')

registry.register(TrelloPlugin)
