from django.http import HttpResponse
from django.http import HttpResponseRedirect
#from django.contrib.auth import authenticate, login
#from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from models import OAuthTempRequestToken, UserAccessToken_LRS
from oauth_consumer.operative import LRS_Auth

import oauth2 as oauth

# Create your views here.
@login_required
def lrs_test_get_statements(request):
    key = '5f3e87886d0f4506b510b3e4b93ef756'
    secret = 'squafiscyAtAAqE6'

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

    return HttpResponse(lrs.transfer_statement())

@login_required
def lrs_test_view(request):
    key = '5f3e87886d0f4506b510b3e4b93ef756'
    secret = 'squafiscyAtAAqE6'

    auth = LRS_Auth(consumer_key=key, secret=secret)

    return HttpResponseRedirect(auth.authenticate(request.user.id))



def lrs_oauth_callback(request):
    import os
    import urlparse

    user_id = request.user.id

    user = User.objects.get(id=user_id)

    request_token = OAuthTempRequestToken.objects.get(user_id=user)
    verifier = request.GET.get('oauth_verifier')

    token = oauth.Token(request_token.token, request_token.secret)
    request_token.delete() #delete temp token
    token.set_verifier(verifier)

    # Get Consumer info #Todo: change (most definitely) (IMPORTANT!!)
    consumer_key = '5f3e87886d0f4506b510b3e4b93ef756'
    consumer_secret = 'squafiscyAtAAqE6'

    client = oauth.Client(oauth.Consumer(consumer_key,consumer_secret),token)

    # Exchange request_token for authed and verified access_token
    resp,content = client.request(os.environ.get('ACCESS_TOKEN_URL'), "POST")
    access_token = dict(urlparse.parse_qsl(content))

    if access_token['oauth_token']:
        UserAccessToken_LRS(user=user, access_token=access_token['oauth_token'],
                            access_token_secret=access_token['oauth_token_secret']).save()



        return HttpResponse("Access Token Successfully attached to account:\nToken: %s\nToken Secret: %s" % (access_token['oauth_token'], access_token['oauth_token_secret']))