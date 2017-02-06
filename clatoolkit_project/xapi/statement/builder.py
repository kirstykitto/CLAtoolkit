import json
import uuid
import ast
import pprint
import datetime

from dataintegration.core.di_utils import *

from xapi_settings import xapi_settings

from xapi.oauth_consumer.operative import LRS_Auth

from tincan import (
    RemoteLRS,
    Statement,
    Agent,
    AgentAccount,
    Verb,
    Activity,
    Context,
    ContextActivities,
    ActivityList,
    LanguageMap,
    ActivityDefinition,
    StateDocument,
    Group,
    Result,
    Score
)

#from resources import lrs_properties

def pretty_print_json(jsn):
    pretty_json = json.dumps(jsn, sort_keys=True, indent=4, separators=(',', ': '))
    return pretty_json

def write_json_tofile(filename, jsn):
    pretty_json = pretty_print_json(jsn)
    with open(filename, 'w') as file_:
        file_.write(pretty_json)

def save_statement_tofile(filename,stm):
    jsn = ast.literal_eval(stm.to_json())
    write_json_tofile(filename, jsn)

def statement_builder(statement_id, actor, verb, object, context, result, authority, timestamp=None):
    statement = None
    if timestamp is None:
        statement = Statement(
            id=statement_id,
            actor=actor,
            verb=verb,
            object=object,
            context=context,
            result=result,
            authority=authority
        )
    else:
        statement = Statement(
            id=statement_id,
            actor=actor,
            verb=verb,
            object=object,
            context=context,
            result=result,
            timestamp=timestamp,
            authority=authority
        )

    return statement


def get_other_contextActivity(obj_id, obj_type, def_name, def_type):
    ret = {}
    definition = {'name': def_name}
    definition['type'] = def_type
    ret['obj_id'] = obj_id
    ret['obj_type'] = obj_type
    ret['definition'] = definition
    return ret


def socialmedia_builder(statement_id, verb, platform, account_name, account_homepage, object_type, object_id,
                        message, tags=[], parent_object_type=None, parent_id=None, rating=None, instructor_name=None,
                        instructor_email=None, team_name=None, unit=None, account_email=None, user_name=None,
                        timestamp=None, other_contexts=[]):

    agentaccount = AgentAccount(name=account_name, home_page=account_homepage)
    actor = Agent(account=agentaccount)

    # XAPI statements can only have one of: AgentAccount, mbox, mboxsha1 or Openid
    #if (account_email is not None):
    #    actor.mbox = account_email
    #if (user_name is not None):
    #    actor.name = user_name

    verb_obj = Verb(id=xapi_settings.get_verb_iri(verb),display=LanguageMap({'en-US': verb}))

    #message = message.decode('utf-8').encode('ascii', 'ignore') #message.decode('utf-8').replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\ud83d", " ").replace(u"\ude09", " ").replace(u"\u00a0l", " ").replace(u"\ud83d", " ").replace(u"\u2026", " ").replace(u"\ude09", " ").replace(u"\u00a0"," ")

    object = Activity(
        id=object_id,
        object_type=object_type,
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': message}),
            type=xapi_settings.get_object_iri(object_type)
        ),
    )

    taglist = []
    for tag in tags:
        tagobject = Activity(
            id='http://id.tincanapi.com/activity/tags/tincan',
            object_type='Activity',
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': tag}),
                type=xapi_settings.get_object_iri('Tag')
                ),
            )
        taglist.append(tagobject)

    # Add "other" in contextActivities
    other_contexts_list = []
    for other in other_contexts:
        other_context_obj = Activity(
            id = other['obj_id'],
            object_type = other['obj_type'],
            definition=ActivityDefinition(
                name = LanguageMap({'en-US': other['definition']['name']}),
                type = other['definition']['type']
            ),
        )
        other_contexts_list.append(other_context_obj)
    taglist.extend(other_contexts_list)


    parentlist = []
    if (verb in ['liked','shared','commented','rated']): #recipe specific config
        parentobject = Activity(
            id=parent_id,
            object_type=parent_object_type,
            )
        parentlist.append(parentobject)
    elif (platform == 'GitHub' or platform.lower() == 'trello'):
        parentobject = Activity(
            id=parent_id,
            object_type=parent_object_type,
            )
        parentlist.append(parentobject)

    courselist = []
    if unit is not None:
        courseobject = Activity(
            id="http://adlnet.gov/expapi/activities/course",
            object_type='Course',
            definition=ActivityDefinition(name=LanguageMap({'en-US': unit.code}), description=LanguageMap({'en-US': "A course/unit of learning hosted on the CLAToolkit"}))
        )
        courselist.append(courseobject)

    instructor = None
    if (instructor_name is not None):
        instructor=Agent(name=instructor_name,mbox=instructor_email)

    team = None
    if (team_name is not None):
        team = Group(Agent(name=team_name), object_type='Group')

    result = None
    if (rating is not None):
        rating_as_float = float(rating)
        result = Result(score=Score(raw=rating_as_float))

    context = Context(
        registration=uuid.uuid4(),
        platform=platform,
        instructor=instructor,
        team=team,
        context_activities=ContextActivities(other=ActivityList(taglist),parent=ActivityList(parentlist),grouping=ActivityList(courselist))
    )

    # Xapi spec requires that the learning provider SHOULD provide the authority
    # Authority is a group with Agent as oauth consumer app where name is token url and homepage is consumer_key
    account = AgentAccount(name=unit.get_lrs_key(), home_page=unit.get_lrs_access_token_url())

    authority = Group(Agent(account=account))

    statement = statement_builder(statement_id,actor, verb_obj, object, context, result,authority, timestamp)

    return statement






