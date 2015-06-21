import json
import uuid
import ast

from dateutil import parser
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
    Group,
    Result,
    Score
)



# from resources import lrs_properties

def pretty_print_json(jsn):
    pretty_json = json.dumps(jsn, sort_keys=True, indent=4, separators=(',', ': '))
    return pretty_json


def write_json_tofile(filename, jsn):
    pretty_json = pretty_print_json(jsn)
    with open(filename, 'w') as file_:
        file_.write(pretty_json)


def save_statement_tofile(filename, stm):
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


def socialmedia_builder(verb, platform, account_name, account_homepage, object_type, object_id, message, tags=[],
                        parent_object_type=None, parent_id=None, rating=None, instructor_name=None,
                        instructor_email=None, team_name=None, course_code=None, account_email=None, user_name=None,
                        timestamp=None):
    verbmapper = {'created': 'http://activitystrea.ms/schema/1.0/create',
                  'shared': 'http://activitystrea.ms/schema/1.0/share',
                  'liked': 'http://activitystrea.ms/schema/1.0/like', 'rated': 'http://id.tincanapi.com/verb/rated',
                  'commented': 'http://adlnet.gov/expapi/verbs/commented'}
    objectmapper = {'Note': 'http://activitystrea.ms/schema/1.0/note',
                    'Tag': 'http://id.tincanapi.com/activitytype/tag',
                    'Article': 'http://activitystrea.ms/schema/1.0/article'}

    agentaccount = AgentAccount(name=account_name, home_page=account_homepage)
    actor = Agent(account=agentaccount)
    if (account_email is not None):
        actor.mbox = account_email
    if (user_name is not None):
        actor.name = user_name

    verb_obj = Verb(id=verbmapper[verb], display=LanguageMap({'en-US': verb}))

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
    if (verb in ['liked', 'shared']):
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
        instructor = Agent(name=instructor_name, mbox=instructor_email)

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
        context_activities=ContextActivities(other=ActivityList(taglist), parent=ActivityList(parentlist),
                                             grouping=ActivityList(courselist))
    )
    timestamp = parser.parse(timestamp)

    statement = statement_builder(actor, verb_obj, object, context, result, timestamp)

    return statement


def dump(obj):
    for attr in dir(obj):
        print "obj.%s = %s" % (attr, getattr(obj, attr))


endpoint_settings = {'url': 'http://transformll-dev.qut.edu.au/data/xAPI/', 'version': "1.0.1",
                     'username': 'a60759b43f86bc5ee1bbc37b40fe02a9f2af0b27',
                     'password': '04d9d51ddd52cfc5ad251c5d9f377a7bb037c63d'}

lrs = RemoteLRS(
    version=endpoint_settings['version'],
    endpoint=endpoint_settings['url'],
    username=endpoint_settings['username'],
    password=endpoint_settings['password']
)
# # microblogging
#
# # create a tweet
# stm = socialmedia_builder(verb='created', platform='Twitter', account_name='aneesha', account_homepage='http://www.twitter.com', object_type='Note', object_id='https://twitter.com/aneesha/status/605894039666171904', message='Just discovered Sirius - a graphical modeling workbench http://www.eclipse.org/sirius/overview.html', account_email="aneesha.bakharia@gmail.com", user_name="Aneesha Bakharia")
# save_statement_tofile("microblogging/microblogging-createtweet.json", stm)
#
# # save our statement to the remote_lrs and store the response in 'response'
# print "Sending"
# res = lrs.save_statement(stm)
#
# print "After send"
# if not res:
#     raise ValueError("statement failed to save")
# #pprint(vars(res))
# #dump(res)
# #dump(res.data)
# #dump(res.request)
# #dump(res.response)
# '''
# # retrieve our statement from the remote_lrs using the id returned in the response
# response = lrs.retrieve_statement(response.content.id)
# print "After receive"
# #print response
#
# if not response.success:
#     raise ValueError("statement could not be retrieved")
# '''
#
# # create a tweet with hashtags and @mentions
# stm = socialmedia_builder(verb='created', platform='Twitter', account_name='aneesha', account_homepage='http://www.twitter.com', object_type='Note', object_id='https://twitter.com/aneesha/status/597971744180174848', message='making social learning (ephemeral social processes) analytics visible @sbuckshum #clatest', tags=['@sbuckshum','#clatest'])
# save_statement_tofile("microblogging/microblogging-tweetwithhashtagsandmentions.json", stm)
#
# # like a tweet
# stm = socialmedia_builder(verb='liked', platform='Twitter', account_name='aneesha', account_homepage='http://www.twitter.com', object_type='Note', object_id='https://twitter.com/DataVizRR/status/605892458413580288', message='9 Designer Tools Everyone Should Know About http://rightrelevance.com/tw/datavizrr/9b88cfbecdf36bcf07bd0e7ba7ca54c0af87a9c4/data%20visualization/data%20visualization')
# save_statement_tofile("microblogging/microblogging-liketweet.json", stm)
#
# # share a tweet
# stm = socialmedia_builder(verb='shared', platform='Twitter', account_name='aneesha', account_homepage='http://www.twitter.com', object_type='Note', object_id='https://twitter.com/BaiduResearch/status/605777762893185026', message='Congrats to Facebook on their new Paris lab. ')
# save_statement_tofile("microblogging/microblogging-sharetweet.json", stm)
#
# # share a tweet and add a description/comment
# stm = socialmedia_builder(verb='shared', platform='Twitter', account_name='aneesha', account_homepage='http://www.twitter.com', object_type='Note', object_id='https://twitter.com/aneesha/status/605898487125803009', message='looks useful for neural nets on theano', parent_id='https://twitter.com/pythontrending/status/605831255490334722', parent_object_type='Note')
# save_statement_tofile("microblogging/microblogging-sharecommenttweet.json", stm)
#
# # content authoring
# # create a blog post
# stm = socialmedia_builder(verb='created', platform='WordPress', account_name='aneesha', account_homepage='http://www.syntaxspectrum.com/', object_type='Article', object_id='http://syntaxspectrum.com/2013/08/5-ways-coursera-has-advanced-the-mooc/', message='5 Ways Coursera has Advanced the MOOC')
# save_statement_tofile("contentcreation/blogging-createblog.json", stm)
#
# # blog post with tags
# stm = socialmedia_builder(verb='created', platform='WordPress', account_name='aneesha', account_homepage='http://www.syntaxspectrum.com/', object_type='Article', object_id='http://syntaxspectrum.com/2013/08/5-ways-coursera-has-advanced-the-mooc/', message='5 Ways Coursera has Advanced the MOOC', tags=['coursera'])
# save_statement_tofile("contentcreation/blogging-createblogwithtags.json", stm)
#
# # Comment on a Blog post
# stm = socialmedia_builder(verb='commented', platform='WordPress', account_name='aneesha', account_homepage='http://www.syntaxspectrum.com/', object_type='Article', object_id='http://syntaxspectrum.com/2013/08/5-ways-coursera-has-advanced-the-mooc/#comment-1086', message='5 Ways Coursera has Advanced the MOOC', parent_id='http://syntaxspectrum.com/2013/08/5-ways-coursera-has-advanced-the-mooc/', parent_object_type='Article' )
# save_statement_tofile("contentcreation/blogging-commentblog.json", stm)
#
# # Rate a Blog post
# stm = socialmedia_builder(verb='rated', platform='WordPress', account_name='aneesha', account_homepage='http://www.syntaxspectrum.com/', object_type='Article', object_id='http://syntaxspectrum.com/2013/08/5-ways-coursera-has-advanced-the-mooc/', message='5 Ways Coursera has Advanced the MOOC', rating='5')
# save_statement_tofile("contentcreation/blogging-rateblog.json", stm)
#
# # Associate with Instructor
# stm = socialmedia_builder(verb='created', platform='Twitter', account_name='aneesha', account_homepage='http://www.twitter.com', object_type='Note', object_id='https://twitter.com/aneesha/status/605894039666171904', message='Just discovered Sirius - a graphical modeling workbench http://www.eclipse.org/sirius/overview.html', instructor_name="Kirty Kitto", instructor_email="email@test.com")
# save_statement_tofile("courseteaminstructor/associateinstructor.json", stm)
#
# # Associate with Team
# #stm = socialmedia_builder(verb='created', platform='Twitter', account_name='aneesha', account_homepage='http://www.twitter.com', object_type='Note', object_id='https://twitter.com/aneesha/status/605894039666171904', message='Just discovered Sirius - a graphical modeling workbench http://www.eclipse.org/sirius/overview.html', team_name="Student Group 1")
# #save_statement("courseteaminstructor/associateteam.json", stm)
#
# # Associate with Course/Unit/Subject
# stm = socialmedia_builder(verb='created', platform='Twitter', account_name='aneesha', account_homepage='http://www.twitter.com', object_type='Note', object_id='https://twitter.com/aneesha/status/605894039666171904', message='Just discovered Sirius - a graphical modeling workbench http://www.eclipse.org/sirius/overview.html', course_code="ABC101")
# save_statement_tofile("courseteaminstructor/associatecourse.json", stm)
#
# context = Context(
#     platform="Twitter"
# )
# '''
# query = {
#     "agent": actor,
#     "verb": verb,
#     "activity": object,
#     "related_activities": True,
#     "related_agents": True,
#     "limit": 2,
# }
# '''
# '''
# verb_obj = Verb(id='http://activitystrea.ms/schema/1.0/create',display=LanguageMap({'en-US': 'created'}))
#
# query = {
#     "verb": verb_obj,
#     "limit": 4,
# }
#
# print "querying statements..."
# response = lrs.query_statements(query)
#
# if not response:
#     raise ValueError("statements could not be queried")
#
# dump(response)
# '''
