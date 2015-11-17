import json
import uuid
import ast
import pprint
import datetime

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

def statement_builder(actor, verb, object, context, result, timestamp=None):
    statement = None
    if timestamp is None:
        statement = Statement(
            actor=actor,
            verb=verb,
            object=object,
            context=context,
            result=result,
        )
    else:
        statement = Statement(
            actor=actor,
            verb=verb,
            object=object,
            context=context,
            result=result,
            timestamp=timestamp
        )
    return statement

def socialmedia_builder(verb, platform, account_name, account_homepage, object_type, object_id, message, tags=[], parent_object_type=None, parent_id=None, rating=None, instructor_name=None, instructor_email=None, team_name=None, course_code=None, account_email=None, user_name=None, timestamp=None):
    verbmapper = {'created': 'http://activitystrea.ms/schema/1.0/create', 'shared': 'http://activitystrea.ms/schema/1.0/share', 'liked': 'http://activitystrea.ms/schema/1.0/like', 'rated': 'http://id.tincanapi.com/verb/rated', 'commented': 'http://adlnet.gov/expapi/verbs/commented'}
    objectmapper = {'Note': 'http://activitystrea.ms/schema/1.0/note', 'Tag': 'http://id.tincanapi.com/activitytype/tag', 'Article': 'http://activitystrea.ms/schema/1.0/article', 'Video': 'http://activitystrea.ms/schema/1.0/video'}

    agentaccount = AgentAccount(name=account_name, home_page=account_homepage)
    actor = Agent(account=agentaccount)
    if (account_email is not None):
        actor.mbox = account_email
    if (user_name is not None):
        actor.name = user_name

    verb_obj = Verb(id=verbmapper[verb],display=LanguageMap({'en-US': verb}))

    #message = message.decode('utf-8').encode('ascii', 'ignore') #message.decode('utf-8').replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\ud83d", " ").replace(u"\ude09", " ").replace(u"\u00a0l", " ").replace(u"\ud83d", " ").replace(u"\u2026", " ").replace(u"\ude09", " ").replace(u"\u00a0"," ")

    object = Activity(
        id=object_id,
        object_type=object_type,
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': message}),
            type=objectmapper[object_type]
        ),
    )

    taglist = []
    for tag in tags:
        tagobject = Activity(
            id='http://id.tincanapi.com/activity/tags/tincan',
            object_type='Activity',
            definition=ActivityDefinition(
                name=LanguageMap({'en-US': tag}),
                type=objectmapper['Tag']
                ),
            )
        taglist.append(tagobject)

    parentlist = []
    if (verb in ['liked','shared','commented','rated']):
        parentobject = Activity(
            id=parent_id,
            object_type=parent_object_type,
            )
        parentlist.append(parentobject)

    courselist = []
    if (course_code is not None):
        courseobject = Activity(
            id=course_code,
            object_type='Course',
            definition=ActivityDefinition(type="http://adlnet.gov/expapi/activities/course")
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

    statement = statement_builder(actor, verb_obj, object, context, result, timestamp)

    return statement
