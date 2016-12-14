from django.http import HttpResponse
from django.http import HttpResponseRedirect
#from django.contrib.auth import authenticate, login
#from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from models import OAuthTempRequestToken, UserAccessToken_LRS, ClientApp
from oauth_consumer.operative import LRS_Auth

import oauth2 as oauth

# Create your views here.
@login_required
def lrs_test_get_statements(request):
    key, secret = get_consumer_key_and_secret()
    params = None

    if request.GET:
        params = dict(request.GET.iterlists())

        keys = params.keys()

        # Convert key:listvalue from querydict to items suitable for dict
        for i in range(len(keys)):
            if type(params[keys[i]]) is 'list' and len(params[keys[i]]) == 1:
                params[keys[i]] = params[keys[i]][0]

    lrs = LRS_Auth()

    return HttpResponse(lrs.get_statement(request.user.id, filters=params))

@login_required
def lrs_test_send(request):

    lrs = LRS_Auth()
    statement = get_test_xAPI()
    return HttpResponse(lrs.transfer_statement(request.user.id, statement = statement))

@login_required
def lrs_test_view(request):
    key, secret = get_consumer_key_and_secret()

    auth = LRS_Auth(consumer_key=key, secret=secret)

    return HttpResponseRedirect(auth.authenticate(request.user.id))



def lrs_oauth_callback(request):
    import os
    import urlparse

    user_id = request.user.id

    print user_id

    user = User.objects.get(id=user_id)

    request_token = OAuthTempRequestToken.objects.get(user_id=user)
    verifier = request.GET.get('oauth_verifier')

    token = oauth.Token(request_token.token, request_token.secret)
    request_token.delete() #delete temp token
    token.set_verifier(verifier)

    # Get Consumer info #Todo: change (most definitely) (IMPORTANT!!)
    consumer_key, consumer_secret = get_consumer_key_and_secret

    client = oauth.Client(oauth.Consumer(consumer_key,consumer_secret),token)

    # Exchange request_token for authed and verified access_token
    resp,content = client.request(os.environ.get('ACCESS_TOKEN_URL'), "POST")
    access_token = dict(urlparse.parse_qsl(content))

    if access_token['oauth_token']:
        UserAccessToken_LRS(user=user, access_token=access_token['oauth_token'],
                            access_token_secret=access_token['oauth_token_secret']).save()



        return HttpResponse("Access Token Successfully attached to account:\nToken: %s\nToken Secret: %s" % (access_token['oauth_token'], access_token['oauth_token_secret']))


def get_consumer_key_and_secret():
    return 'a80338a09b1d4fa6a431de5604560821', '2wHSI0kcKTRRnPN5'


def get_test_xAPI():
    return """{
        "id": "dc382d58-173a-4722-886d-7da23a725732",
        "verb": {
            "display": {
                "en-US": "created"
            },
            "id": "http://www.w3.org/ns/activitystreams#Create"
        },
        "timestamp": "2016-11-01T08:33:28.423000+00:00",
        "object": {
            "definition": {
                "type": "http://activitystrea.ms/specs/json/schema/activity-schema.html#task",
                "name": {
                    "en-US": "Add after removing board ID from the toolkit..."
                }
            },
            "id": "http://www.test.com/5818535876f64eded095ae82",
            "objectType": "Activity"
        },
        "actor": {
            "account": {
                "homePage": "http://www.trello.com/",
                "name": "koji"
            },
            "objectType": "Agent"
        },
        "authority": {
        "member": [
            {
                "mbox": "mailto:zak@zak.com",
                "name": "zak",
                "objectType": "Agent"
            },
            {
                "account": {
                    "homePage": "http://example.com/XAPI/OAuth/token/",
                    "name": "4a77c7336e92425d9e56ec7bdb58223d"
                },
                "objectType": "Agent"
            }
        ],
        "objectType": "Group"
    },
        "version": "1.0.1",
        "context": {
            "platform": "Trello",
            "contextActivities": {
                "other": [],
                "parent": [
                    {
                        "id": "http://test.com/aaa",
                        "objectType": "Activity"
                    }
                ],
                "grouping": [
                    {
                        "definition": {
                            "name": {
                                "en-US": "TEST-UNIT"
                            },
                            "description": {
                                "en-US": "TEST-UNIT"
                            }
                        },
                        "id": "http://test.com/TEST-UNIT",
                        "objectType": "Activity"
                    }
                ]
            },
            "registration": "dc382d58-173a-4722-886d-7da68a925924"
        }
    }"""