__author__ = 'zak'

import json
import uuid
import ast
import pprint
import datetime

from di_utils import *

from clatoolkit.models import LearningRecord,SocialRelationship

from xapi.statement.builder import socialmedia_builder, pretty_print_json
from xapi.statement.xapi_settings import xapi_settings

from xapi.oauth_consumer.operative import LRS_Auth
#from dataintegration.core.utils import check_ifnotinlocallrs


def insert_share(user, post_id, share_id, comment_message, comment_created_time, unit, platform, platform_url, tags=(),
                 parent_user=None, parent_external_user=None):

    if check_ifnotinlocallrs(unit, platform, share_id):
        # Setup statement builder parameters and lrs using default lrs. TODO: Institutions required in xapi maybe?
        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        _parent_user = parent_user if parent_user else parent_external_user
        statement_id = get_uuid4()

        #lrs.xapi = the "transaction" uuid
        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=xapi_settings.VERB_SHARED, platform=platform, user=user, 
                             platformid=share_id, platformparentid=post_id, parent_user=parent_user,
                             parent_user_external=parent_external_user, message=comment_message,
                             datetimestamp=comment_created_time)
        lrs.save()

        #Send xapi to lrs or cache for later
        stm = socialmedia_builder(statement_id=statement_id, verb=xapi_settings.VERB_SHARED, platform=platform, 
          account_name=account_name, account_homepage=platform_url, object_type=xapi_settings.OBJECT_NOTE, 
          object_id=share_id, message=comment_message, parent_id=post_id, parent_object_type=xapi_settings.OBJECT_NOTE, 
          timestamp=comment_created_time, unit=unit, tags=tags )
        jsn = stm.to_json()
        #Transfer xapi to lrs TODO: Handle caching for failed sends
        # print 'Sending xapi..'
        status,content = lrs_client.transfer_statement(user.id, statement=jsn)

        # print 'Tried to send xapi to lrs: status %s, response: %s' % (status,content)

        sr = SocialRelationship(verb=xapi_settings.VERB_SHARED, from_user=user, to_user=parent_user,
                                to_external_user=parent_external_user, platform=platform, message=comment_message,
                                datetimestamp=comment_created_time, unit=unit, platformid=share_id)
        sr.save()

def insert_post(user, post_id, message, created_time, unit, platform, platform_url, tags=()):
    # verb = 'created'
    verb = xapi_settings.VERB_CREATED

    #TODO: update for lrs connection as it happens
    if check_ifnotinlocallrs(unit, platform, post_id, user, verb):

        #Setup statment builder with param and build lrs using defualt rs
        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        statement_id = get_uuid4()

        #lrs.xapi = the "transaction" uuid
        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=verb, platform=platform, user=user, 
                            platformid=post_id, message=message, datetimestamp=created_time)
        lrs.save()

        #Transfer xapi to lrs of cache for later
        stm = socialmedia_builder(statement_id=statement_id, verb=verb, platform=platform, account_name=account_name,
                                  account_homepage=platform_url, object_type=xapi_settings.OBJECT_NOTE, 
                                  object_id=post_id, message=message, timestamp=created_time, unit=unit, tags=tags)
        jsn = stm.to_json()
        # print 'sending xapi... '
        # print jsn

        status,content = lrs_client.transfer_statement(user.id, statement=jsn)

        # print 'in insert_post(): Response status/code from LRS: %s/%s' % (status, content)

        for tag in tags:
            if tag[0] == "@":
                # If the user exists, use their user object else reference them as an external user
                if username_exists(tag[1:], unit, platform):
                    to_user = get_user_from_screen_name(tag[1:], platform)
                    external_user = None
                else:
                    to_user = None
                    external_user = tag[1:]

                sr = SocialRelationship(verb=xapi_settings.VERB_MENTIONED, from_user=user, to_user=to_user,
                                        to_external_user=external_user, platform=platform, message=message,
                                        datetimestamp=created_time, unit=unit, platformid=post_id)
                sr.save()


# def insert_blogpost(usr_dict, post_id,message,from_name,from_uid, created_time, course_code, platform, platform_url, tags=[]):
def insert_blogpost(user, post_id, message, from_name, from_uid, created_time, unit, platform, platform_url, tags=[]):
    if check_ifnotinlocallrs(unit, platform, post_id):
        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        statement_id = get_uuid4()

        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=xapi_settings.VERB_CREATED, 
                            platform=platform, user=user, platformid=post_id, message=message, datetimestamp=created_time)
        lrs.save()

        #Transfer xapi to lrs of cache for later
        stm = socialmedia_builder(statement_id=statement_id, verb=xapi_settings.VERB_CREATED, platform=platform, 
                                  account_name=account_name, account_homepage=platform_url, 
                                  object_type=xapi_settings.OBJECT_ARTICLE, object_id=post_id, message=message, 
                                  timestamp=created_time, unit=unit, tags=tags)

        jsn = stm.to_json()
        status,content = lrs_client.transfer_statement(user.id, statement=jsn)

        for tag in tags:
            if tag[0]=="@":
                to_user = get_username_fromsmid(tag[1:], platform)

                sr = SocialRelationship(verb=xapi_settings.VERB_MENTIONED, from_user=user, to_user=to_user,
                                        platform=platform, message=message, datetimestamp=created_time, 
                                        unit=unit, platformid=post_id)
                sr.save()


    # if check_ifnotinlocallrs(course_code, platform, post_id):

    #     stm = socialmedia_builder(verb='created', platform=platform, account_name=from_name, 
    #       account_homepage=platform_url, object_type='Article', object_id=post_id, message=message, 
    #       timestamp=created_time, account_email=usr_dict['email'], user_name=from_uid, course_code=course_code, tags=tags)

    #     jsn = ast.literal_eval(stm.to_json())
    #     stm_json = pretty_print_json(jsn)
    #     lrs = LearningRecord(xapi=stm_json, course_code=course_code, verb='created', platform=platform, 
    #       username=from_name, platformid=post_id, message=message, datetimestamp=created_time)
    #     lrs.save()
    #     for tag in tags:
    #         if tag[0]=="@":
    #             socialrelationship = SocialRelationship(verb = "mentioned", 
    #               fromusername=get_username_fromsmid(from_name,platform), 
    #               tousername=get_username_fromsmid(tag[1:],platform), platform=platform, message=message, 
    #               datetimestamp=created_time, course_code=course_code, platformid=post_id)

    #             socialrelationship.save()


def insert_like(user, object_id, message, unit, platform, platform_url, parent_id, parent_object_type, created_time=None, 
                parent_user=None, parent_user_external=None):
    verb = xapi_settings.VERB_LIKED

    if check_ifnotinlocallrs(unit, platform, object_id, user, verb):
        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        statement_id = get_uuid4()

        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=verb, platform=platform, user=user, 
                             platformid=object_id, message=message, platformparentid=object_id, parent_user=parent_user,
                             parent_user_external=parent_user_external, datetimestamp=created_time)
        lrs.save()

        sr = SocialRelationship(verb=verb, from_user=user, to_user=parent_user,
                                to_external_user=parent_user_external, platform=platform, message=message,
                                datetimestamp=created_time, unit=unit, platformid=object_id)
        sr.save()

        # Send xAPI to LRS
        stm = socialmedia_builder(statement_id=statement_id, verb=verb, platform=platform, 
                                  account_name=account_name, account_homepage=platform_url, 
                                  object_type=xapi_settings.OBJECT_NOTE, object_id=object_id, message=message, 
                                  parent_id=parent_id, parent_object_type=parent_object_type, 
                                  timestamp=created_time, unit=unit)
        jsn = stm.to_json()
        status,content = lrs_client.transfer_statement(user.id, statement=jsn)


# Not used?
# def insert_blogcomment(usr_dict, post_id, comment_id, comment_message, comment_from_uid, comment_from_name, comment_created_time, course_code, platform, platform_url, shared_username=None, shared_displayname=None):

#     #print "1: %s\n 2: %s\n 3: %s\n 4: %s" % (comment_from_uid, comment_from_name,shared_username,shared_displayname)

#     if check_ifnotinlocallrs(course_code, platform, comment_id):
#         if shared_displayname is not None:
#             stm = socialmedia_builder(verb='commented', platform=platform, account_name=comment_from_uid, account_homepage=platform_url, object_type='Note', object_id=comment_id, message=comment_message, parent_id=post_id, parent_object_type='Note', timestamp=comment_created_time, account_email=usr_dict['email'], user_name=comment_from_name, course_code=course_code )
#             jsn = ast.literal_eval(stm.to_json())
#             stm_json = pretty_print_json(jsn)
#             lrs = LearningRecord(xapi=stm_json, course_code=course_code, verb='commented', platform=platform, username=get_username_fromsmid(comment_from_uid, platform), platformid=comment_id, platformparentid=post_id, parentusername=get_username_fromsmid(shared_displayname,platform), parentdisplayname=shared_displayname, message=comment_message, datetimestamp=comment_created_time)
#             lrs.save()
#             print "COMMENT SAVED!"
#             socialrelationship = SocialRelationship(verb = "commented", fromusername=get_username_fromsmid(comment_from_uid,platform), tousername=get_username_fromsmid(shared_username,platform), platform=platform, message=comment_message, datetimestamp=comment_created_time, course_code=course_code, platformid=comment_id)
#             socialrelationship.save()


def insert_comment(user, post_id, comment_id, comment_message, comment_created_time, unit, platform, platform_url,
                   parent_user=None, parent_user_external=None, other_contexts = []):

    if check_ifnotinlocallrs(unit, platform, comment_id):
        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        statement_id = get_uuid4()

        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=xapi_settings.VERB_COMMENTED, platform=platform, 
                             user=user, platformid=comment_id, platformparentid=post_id, parent_user=parent_user,
                             parent_user_external=parent_user_external, message=comment_message,
                             datetimestamp=comment_created_time)
        lrs.save()

        sr = SocialRelationship(verb=xapi_settings.VERB_COMMENTED, from_user=user, to_user=parent_user,
                                to_external_user=parent_user_external, platform=platform, message=comment_message,
                                datetimestamp=comment_created_time, unit=unit, platformid=comment_id)
        sr.save()

        stm = socialmedia_builder(statement_id=statement_id, verb=xapi_settings.VERB_COMMENTED, platform=platform, 
            account_name=account_name, account_homepage=platform_url, object_type=xapi_settings.OBJECT_NOTE, 
            object_id=comment_id, message=comment_message, parent_id=post_id, parent_object_type=xapi_settings.OBJECT_NOTE, 
            timestamp=comment_created_time, unit=unit, other_contexts = other_contexts)
            
        jsn = stm.to_json()
        status,content = lrs_client.transfer_statement(user.id, statement=jsn)

# Diigo is the only one that's supposed to call this method, but caller is commented out... 
# Is this method not needed anymore??
def insert_bookmark(usr_dict, post_id,message,from_name,from_uid, created_time, course_code, platform, platform_url, tags=[]):
    if check_ifnotinlocallrs(course_code, platform, post_id):
        stm = socialmedia_builder(verb='created', platform=platform, account_name=from_uid, account_homepage=platform_url, object_type='Bookmark', object_id=post_id, message=message, timestamp=created_time, account_email=usr_dict['email'], user_name=from_name, course_code=course_code, tags=tags)
        jsn = ast.literal_eval(stm.to_json())
        stm_json = pretty_print_json(jsn)
        lrs = LearningRecord(xapi=stm_json, course_code=course_code, verb='created', platform=platform, username=get_username_fromsmid(from_uid, platform), platformid=post_id, message=message, datetimestamp=created_time)
        lrs.save()



def insert_commit(user, commit_id, message, from_uid, from_name, committed_time, 
    parent_id, unit, platform, platform_id, commit_username, account_homepage, tags=[], other_contexts = []):
    if check_ifnotinlocallrs(unit, platform, platform_id):
        verb = xapi_settings.VERB_CREATED
        object_type = xapi_settings.OBJECT_COLLECTION
        parent_obj_type = xapi_settings.OBJECT_COLLECTION

        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        statement_id = get_uuid4()

        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=verb, platform=platform, user=user, 
            platformid=platform_id, platformparentid=parent_id, message=message, datetimestamp=committed_time)
        lrs.save()

        # sr = SocialRelationship(verb = verb, from_user=user, to_user=get_uid_fromsmid(commit_username, platform),
        #                         platform=platform, message=message, 
        #                         datetimestamp=committed_time, unit=unit, platformid=commit_id)
        # sr.save()

        stm = socialmedia_builder(statement_id=statement_id, verb=verb, platform=platform, 
            account_name=account_name, account_homepage=account_homepage, object_type=object_type, 
            object_id=commit_id, message=message, parent_id=parent_id, parent_object_type=parent_obj_type, 
            timestamp=committed_time, unit=unit, tags=tags, other_contexts = other_contexts)

        jsn = stm.to_json()
        status,content = lrs_client.transfer_statement(user.id, statement=jsn)

# def insert_commit(user, repo_id, commit_id, message, committed_time, unit, platform, committer=None):
#     if check_ifnotinlocallrs(unit, platform, commit_id):
#         verb = "created"

#         lrs = LearningRecord(xapi=None, unit=unit, verb=verb, platform=platform, user=user, platformid=commit_id,
#                              platformparentid=repo_id, message=message, datetimestamp=committed_time)
#         lrs.save()



def insert_file(user, file_id, message, from_uid, from_name, committed_time, unit, parent_id, platform, platform_id, 
    platform_parentid, verb, commit_username, account_homepage, tags=[], other_contexts = []):
    if check_ifnotinlocallrs(unit, platform, platform_id):
        obj = xapi_settings.OBJECT_FILE
        parentObj = xapi_settings.OBJECT_COLLECTION

        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        statement_id = get_uuid4()

        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=verb, platform=platform, 
            user=user, platformid=platform_id, platformparentid=platform_parentid, 
            message=message, datetimestamp=committed_time)
        lrs.save()

        # sr = SocialRelationship(verb = verb, from_user=user, to_user=get_uid_fromsmid(commit_username, platform),
        #                         platform=platform, message=message, 
        #                         datetimestamp=committed_time, unit=unit, platformid=file_id)
        # sr.save()

        stm = socialmedia_builder(statement_id=statement_id, verb=verb, platform=platform, 
            account_name=account_name, account_homepage=account_homepage, object_type=obj, 
            object_id=file_id, message=message, parent_id=parent_id, parent_object_type=parentObj, 
            timestamp=committed_time, unit=unit, tags=tags, other_contexts = other_contexts)

        jsn = stm.to_json()
        status,content = lrs_client.transfer_statement(user.id, statement=jsn)


# def insert_file(user, commit_id, file_id, message, committed_time, unit, platform, verb):
#     if check_ifnotinlocallrs(unit, platform, file_id):
#         lrs = LearningRecord(xapi=None, unit=unit, verb=verb, platform=platform, user=user, platformid=file_id,
#                              platformparentid=commit_id, message=message, datetimestamp=committed_time)
#         lrs.save()



def insert_issue(user, issue_id, verb, object_type, parent_object_type, message, from_name, from_uid, created_time, 
    unit, parent_id, platform, platform_id, account_homepage, shared_displayname=None, tags=[], other_contexts = []):
    if check_ifnotinlocallrs(unit, platform, platform_id):
        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        statement_id = get_uuid4()

        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=verb, platform=platform, user=user,
                             platformid=platform_id, platformparentid=parent_id, 
                             message=message, datetimestamp=created_time)
        lrs.save()

        stm = socialmedia_builder(statement_id=statement_id, verb=verb, platform=platform, 
            account_name=from_uid, account_homepage=account_homepage, object_type=object_type, 
            object_id=issue_id, message=message, parent_id=parent_id, parent_object_type=parent_object_type, 
            timestamp=created_time, unit=unit, tags=tags, other_contexts = other_contexts)
        
        jsn = stm.to_json()
        status,content = lrs_client.transfer_statement(user.id, statement=jsn)

        """
        for tag in tags:
            if tag[0]=="@":
                socialrelationship = SocialRelationship(
                    verb = "mentioned", fromusername=get_username_fromsmid(from_uid,platform), 
                    tousername=get_username_fromsmid(tag[1:],platform), 
                    platform=platform, message=message, datetimestamp=created_time, 
                    course_code=course_code, platformid=platform_id)
                socialrelationship.save()
        """

# def insert_issue(user, repo_id, issue_id, message, created_time, unit, platform):
#     if check_ifnotinlocallrs(unit, platform, issue_id):
#         verb = 'created'

#         lrs = LearningRecord(xapi=None, unit=unit, verb=verb, platform=platform, platformid=issue_id, user=user,
#                              platformparentid=repo_id, message=message, datetimestamp=created_time)
#         lrs.save()
#         """
#         for tag in tags:
#             if tag[0]=="@":
#                 socialrelationship = SocialRelationship(
#                     verb = "mentioned", fromusername=get_username_fromsmid(from_uid,platform),
#                     tousername=get_username_fromsmid(tag[1:],platform),
#                     platform=platform, message=message, datetimestamp=created_time,
#                     course_code=course_code, platformid=platform_id)
#                 socialrelationship.save()
#         """


def insert_task(user, task_id, task_name, task_from_uid, task_from_name, task_created_time, unit, platform, 
                platform_url, list_id=None, other_contexts = []):

    if check_ifnotinlocallrs(unit, platform, task_id):
        lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())
        account_name = user.userprofile.get_username_for_platform(platform)
        statement_id = get_uuid4()

        lrs = LearningRecord(statement_id=statement_id, unit=unit, verb=xapi_settings.VERB_CREATED, platform=platform, 
                             user=user, platformid=task_id, message=task_name, datetimestamp=task_created_time)
        lrs.save()

        stm = socialmedia_builder(statement_id=statement_id, verb=xapi_settings.VERB_CREATED, platform=platform, 
          account_name=task_from_uid, account_homepage=platform_url,object_type=xapi_settings.OBJECT_TASK, 
          object_id=task_id, message=task_name, timestamp=task_created_time, unit=unit, 
          other_contexts = other_contexts)

        jsn = stm.to_json()
        status,content = lrs_client.transfer_statement(user.id, statement=jsn)

        #maybe we can capture commenting behaviours between user/caard somehow?

def insert_added_object(usr_dict, target_id, object_id, object_text, obj_from_uid, obj_from_name, obj_created_time,
                        course_code, platform, platform_url, obj_type, shared_usrname=None, shared_displayname=None,
                        other_contexts = []):
    if check_ifnotinlocallrs(course_code, platform, object_id):
        if shared_displayname is not None:
            stm = socialmedia_builder(verb='added', platform=platform, account_name=obj_from_uid, account_homepage=platform_url,
                                      object_type=obj_type, object_id=object_id, message=object_text, parent_id=target_id,
                                      parent_object_type='Task', timestamp=obj_created_time, account_email=usr_dict['email'],
                                      user_name=obj_from_name, course_code=course_code, other_contexts = other_contexts)
            jsn = ast.literal_eval(stm.to_json())
            stm_jsn = pretty_print_json(jsn)
            lrs = LearningRecord(xapi=stm_jsn, course_code=course_code, verb='added', platform=platform,
                                 username=get_username_fromsmid(obj_from_uid, platform),
                                 platformid=object_id, platformparentid=target_id,
                                 parentusername=get_username_fromsmid(shared_displayname,platform),
                                 parentdisplayname=shared_displayname, message=object_text,
                                 datetimestamp=obj_created_time)
            lrs.save()

            '''Maybe social relationship stuff...
            '''

def insert_updated_object(usr_dict, object_id, object_text, obj_updater_uid, obj_updater_name, obj_update_time,
                          course_code, platform, platform_url, obj_type, obj_parent=None, obj_parent_type=None,
                          other_contexts = []):
    if check_ifnotinlocallrs(course_code, platform, object_id):
        if obj_parent is not None:
            stm = socialmedia_builder(verb='updated', platform=platform, account_name=obj_updater_uid, account_homepage=platform_url,
                                      object_type=obj_type, object_id=object_id, message=object_text, parent_id=obj_parent,
                                      parent_object_type=obj_parent_type, timestamp=obj_update_time, account_email=usr_dict['email'],
                                      user_name=obj_updater_name, course_code=course_code, other_contexts = other_contexts)
            jsn = ast.literal_eval(stm.to_json())
            stm_jsn = pretty_print_json(jsn)
            lrs = LearningRecord(xapi=stm_jsn, course_code=course_code, verb='updated', platform=platform,
                                 username=get_username_fromsmid(obj_updater_uid, platform),
                                 platformid=object_id, platformparentid=obj_parent,
                                 message=object_text, datetimestamp=obj_update_time)
            lrs.save()

def insert_closedopen_object(usr_dict, object_id, object_text, obj_updater_uid, obj_updater_name, obj_update_time,
                          course_code, platform, platform_url, obj_type, verb, obj_parent=None, obj_parent_type=None,
                          other_contexts = []):
    if check_ifnotinlocallrs(course_code, platform, object_id):
        if obj_parent is not None:
            stm = socialmedia_builder(verb=verb, platform=platform, account_name=obj_updater_uid, account_homepage=platform_url,
                                      object_type=obj_type, object_id=object_id, message=object_text, parent_id=obj_parent,
                                      parent_object_type=obj_parent_type, timestamp=obj_update_time, account_email=usr_dict['email'],
                                      user_name=obj_updater_name, course_code=course_code, other_contexts = other_contexts)
            jsn = ast.literal_eval(stm.to_json())
            stm_jsn = pretty_print_json(jsn)
            lrs = LearningRecord(xapi=stm_jsn, course_code=course_code, verb=verb, platform=platform,
                                 username=get_username_fromsmid(obj_updater_uid, platform),
                                 platformid=object_id, platformparentid=obj_parent, message=object_text,
                                 datetimestamp=obj_update_time)
            lrs.save()



"""def insert_comment(usr_dict, post_id, comment_id, comment_message, comment_from_uid, comment_from_name, comment_created_time,
course_code, platform, platform_url, shared_username=None, shared_displayname=None):
    print "Insert comment -  from %s to %s" % (comment_from_uid,shared_displayname)
    if check_ifnotinlocallrs(course_code, platform, comment_id):
        if shared_displayname is not None:
            stm = socialmedia_builder(verb='commented', platform=platform, account_name=comment_from_uid, account_homepage=platform_url,
            object_type='Note', object_id=comment_id, message=comment_message, parent_id=post_id, parent_object_type='Note', timestamp=comment_created_time, account_email=usr_dict['email'], user_name=comment_from_name, course_code=course_code )
            jsn = ast.literal_eval(stm.to_json())
            stm_json = pretty_print_json(jsn)
            lrs = LearningRecord(xapi=stm_json, course_code=course_code, verb='commented', platform=platform, username=get_username_fromsmid(comment_from_name, platform), platformid=comment_id, platformparentid=post_id, parentusername=get_username_fromsmid(shared_displayname,platform), parentdisplayname=shared_displayname, message=comment_message, datetimestamp=comment_created_time)
            lrs.save()
            print "COMMENT SAVED!"
            socialrelationship = SocialRelationship(verb = "commented", fromusername=get_username_fromsmid(comment_from_uid,platform), tousername=get_username_fromsmid(shared_username,platform), platform=platform, message=comment_message, datetimestamp=comment_created_time, course_code=course_code, platformid=comment_id)
            socialrelationship.save()"""
