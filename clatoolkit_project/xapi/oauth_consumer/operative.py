__author__ = 'zak'

import os
import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from connector import AuthRequest
from xapi.models import OAuthTempRequestToken, ClientApp
from xapi.models import UserAccessToken_LRS as AccessToken

"""
This file contains code used to connect to an LRS via Oauth and
retreive various access tokens.

Utilising OAuth 1.0, the flow used to connect to the LRS is as follows:

Send auth request to LRS with callback as parameter, and:
oauth_consumer_key, oauth_signature_method, oauth_signature, oauth_nonce, oauth_timestamp
as headers. The oauth_signature is created using basic signature string hashed using
HMAC-SHA1 digest

GET http://lrs/xapi/OAuth/initiate?oauth_callback=http://callback_url

If this process if successful, the LRS will respond with:
oauth_token, oauth_token_secret, and oauth_callback_confirmed. Next, we exchange the token
with the LRS for an access token with the oauth_token and oauth_callback as params.

GET http://lrs/xapi/OAuth/authorize?oauth_token=token_code&oauth_callback=http://callback_url

In this step, the LRS will redirect to the given callback with a oauth_verifier code where the user
confirms the authorization process.

GET http://lrs/xapi/OAuth/token

Upon the user accepting, a final request is sent back to the lrs with:
oauth_consumer_key, oauth_token, oauth_signature_method, oauth_signature, oauth_verifier, oauth_timestamp,
oauth_nonce. Once again, the signature is created by hashing the basic signature string via HMAC-SHA1. If
this process succeeds, the LRS will return the access token to make authorized requests.

"""

class LRS_Auth(object):

    def __init__(self, consumer_key=None, secret=None, **kwargs):

        # LRS API Endpoints TODO: make configurable via GUI
        LOCAL = True
        SCHEME = 'http' if LOCAL else 'https' #http
        SERVER = '127.0.0.1' if LOCAL else 'lrs.beyondlms.org'
        PORT = '8000' if LOCAL else '443' #8000

        self.REQUEST_TOKEN_URL = '%s://%s:%s%s' % (SCHEME,SERVER,PORT,'/xapi/OAuth/initiate')
        self.ACCESS_TOKEN_URL = '%s://%s:%s%s' % (SCHEME,SERVER,PORT,'/xapi/OAuth/token')
        self.AUTHORIZATION_URL = '%s://%s:%s%s' % (SCHEME,SERVER,PORT, '/xapi/OAuth/authorize')
        self.CALLBACK_URL = 'http://localhost:8080/xapi/lrsauth_callback'

        # LRS Resource URL(s)
        self.STATEMENTS_URL = '%s://%s:%s%s' % (SCHEME,SERVER,PORT,'/xapi/statements')

        # Error Validation
        if not consumer_key:

            if secret: # Has no consumer_key, but instantiated with a secret
                raise ValueError('Cannot Create LRS Auth Client. Both consumer key and secret must be supplied. Given: secret')

            # No consumer key or secret key - use default lrs provider (lrs.beyondlms.org)
            default_lrs = ClientApp.objects.get(provider='default_lrs')

            self.CONSUMER_KEY = default_lrs.get_key()
            self.CONSUMER_SECRET = default_lrs.get_secret()

        # Allow for building LRS Auth Client with only consumer key (if secret is known in db)
        elif consumer_key and not secret:

            # Try to get lrs provider using only consumer key
            try:
                lrs_provider = ClientApp.objects.get(i=consumer_key)

                self.CONSUMER_KEY = lrs_provider.get_key()
                self.CONSUMER_SECRET = lrs_provider.get_secret()

            except ObjectDoesNotExist:
                raise ValueError('Cannot get LRS Provider with consumer key: %s' % consumer_key)

        elif consumer_key and secret: # Parameters were sent

            self.CONSUMER_KEY = consumer_key
            self.CONSUMER_SECRET = secret

        # Save Access-token exchange url to env TODO: Find a better way to handle this.
        os.environ['ACCESS_TOKEN_URL'] = self.ACCESS_TOKEN_URL

    def get_statement(self, user_id, filters=None, limit=None):
        user = User.objects.get(id=user_id)
        t = AccessToken.objects.get(user_id=user)

        consumer = AuthRequest(self.CONSUMER_KEY,self.CONSUMER_SECRET,
                               token=t.access_token, token_secret=t.access_token_secret)

        kwargs = {}
        #extract filters
        if filters is not None:
            kwargs['filters'] = filters

        (code,content) = consumer.request(self.STATEMENTS_URL, **kwargs)

        if str(code) != '200':
            raise Exception("Could not get xapi statments. Status: %s, Message: %s" % (code,content))
        else:
            return content



    # function for sending xapi statements to the LRS
    # requires user_id to retreive user access token
    # TODO: Implement batch sends
    def transfer_statement(self, user_id, statement=None, batch=False):

        if not batch and statement is not None:
            #Get user access token
            user = User.objects.get(id=user_id)
            t = AccessToken.objects.get(user_id=user)

            consumer = AuthRequest(self.CONSUMER_KEY,self.CONSUMER_SECRET,
                                   token=t.access_token,token_secret=t.access_token_secret)
            (code, content) = consumer.request(self.STATEMENTS_URL, data=statement)
            
            # ADL_LRS returns status 204 for successful statement transfers
            if str(code) != ('200' or '204'):
                raise Exception("Could not send xapi statement with status code %s. Message: %s" % (code,content))
            else:
                return 'HTTP Code: %s, content: %s' % (code, content)


    def authenticate(self, user_id):

        import urlparse

        # Create a consumer utilising the key and secret provided by lrs
        # Because this is an auth-flow we need to supply a callback url
        consumer = AuthRequest(self.CONSUMER_KEY,self.CONSUMER_SECRET,callback=self.CALLBACK_URL)

        # 1st Leg: Get temp request token to exchange for access token
        #print 'Getting temp req token from: %s' % self.REQUEST_TOKEN_URL

        (status_code,content) = consumer.request(self.REQUEST_TOKEN_URL)

        # We're expecting a dict (request/response)
        # a string here likely is an error string
        #if type(resp) is str:
        #    raise Exception(resp)

        #print 'Got response code: %s' % resp.getcode()

        # status code 200 to let us know everything is a-okay
        if  status_code != 200:
            raise Exception("Unexpected server response: %s. Message: %s" % (status_code,content))

        # parse qsl and get returned data
        request_token = dict(urlparse.parse_qsl(content))

        #print "Request Token:"
        #print "     - oauth_token           = %s" % request_token['oauth_token']
        #print "     - oauth_token_secret    = %s" % request_token['oauth_token_secret']
        #print "     - callback_confirmed    = %s" % request_token
        #print

        # Store temp token and and temp token_secret for 3rd leg of auth
        # in the 3rd leg, we exchange this temp token & secret for authorized access_token
        user = User.objects.get(id=user_id)
        tmp_reqToken = OAuthTempRequestToken(user_id=user_id, token=request_token['oauth_token'], secret=request_token['oauth_token_secret'])
        tmp_reqToken.save()

        # 2nd leg: Redirect to lrs to allow user to confirm access token permissions
        return self.lrs_2ndstep_redirect(request_token['oauth_token'], self.CALLBACK_URL)

    def lrs_2ndstep_redirect(self, token, callback):
        oauth_token_param = '?oauth_token=%s' % token
        oauth_callback_param = '&oauth_callback=%s' % callback

        #3rd leg found in views.py
        return self.AUTHORIZATION_URL+oauth_token_param+oauth_callback_param





#class DefaultLRS():












###################################
##           Graveyard           ##
###################################

"""import time
import oauth.oauth as oauth
import requests
import urlparse
import cgi
from urllib import urlencode

#Local/production settings
LOCAL = True
SCHEME = 'http' if LOCAL else 'https' #http
SERVER = '127.0.0.1' if LOCAL else 'lrs.beyondlms.org'
PORT = '8000' if LOCAL else '443' #8000

# fake urls for test server
REQUEST_TOKEN_URL = '%s://%s:%s%s' % (SCHEME,SERVER,PORT,'xapi/oauth/initiate')
ACCESS_TOKEN_URL = '%s://%s:%s%s' % (SCHEME,SERVER,PORT,'xapi/oauth/token')
AUTHORIZATION_URL = '%s://%s:%s%s' % (SCHEME,SERVER,PORT, 'xapi/oauth/authorize')
CALLBACK_URL = 'oob'
RESOURCE_URL = '%s://%s:%s%s' % (SCHEME,SERVER,PORT, 'xapi/statements')

# include scope if required
INCLUDE_SCOPE = False

# scope (space delimited)
SCOPE = {"scope": "statements/write define statements/read/mine"}

# error file location
ERROR_FILE = '/error.html'

class SimpleOAuthClient(oauth.OAuthClient):

    def __init__(self, request_token_url='', access_token_url='', authorization_url=''):
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorization_url = authorization_url

    def fetch_request_token(self, oauth_request):
        path = oauth_request.to_url()

        if (INCLUDE_SCOPE):
            path = path + "&%s" % urlencode(SCOPE)

        response = requests.get(path, header=oauth_request.to_header(), verify=False)

        if response.status_code != 200:
            print 'Failure: %s' % response.status_code

            f = open(ERROR_FILE, 'w')
            f.write(response.content)
            f.close()
            print 'Error written to %s' % ERROR_FILE

        return oauth.OAuthToken.from_string(response.content)

    def fetch_access_token(self, oauth_request):
        response = requests.get(oauth_request.to_url(), headers=oauth_request.to_header(), verify=False)

        return oauth.OAuthToken.from_string(response.content)

    def authorize_token(self, oauth_request):
        response = requests.get(oauth_request.to_url(), allow_rediects=False, verify=False)

        # rediect code expected
        if response.status_code != 200:
            if response.status_code > 300  and response.status_code < 400:
                newurl = response.headers['location']
                parts = urlparse.urlparse(newurl)[2:]

                print parts[2]

                u = urlparse.urlparse(parts[2])

                return 'http://localhost:8000?oauth_verifier=%s' % raw_input("go to %s, verify, enter PIN here: " % u['next'])

            else:
                print "Failure: %s" % response.status_code
                f = open(ERROR_FILE, 'w')
                f.write(response.content)
                f.close()
                print "text written to %s" % ERROR_FILE
                raise Exception("Something didnt work right\nresponse: %s -- %s" % (response.status_code, response.content))
"""
