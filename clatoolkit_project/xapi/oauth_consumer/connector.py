__author__ = 'zak'

import requests
import time
import json
from urllib import urlencode
import urllib

"""
AuthRequest: a quick wrapper class to create signed oauth requests to lrs

Note: I did this because the ADL_LRS does not comply with either OAuth 1.0 or 2.0 specs
        rather, a mix of the two was implemented. Which made it hard to access much using
        regular OAuth libraries
"""

class AuthRequest():

    def __init__(self, consumer_key,  secret, callback=None, token=None, token_secret=None):

        # Consumer secret is used in every signed oauth request
        if not secret:
            raise ValueError('Consumer secret required')

        self.callback = callback # We always specify a callback for auth-flow requests
        self.secret = secret
        self.consumer_key = consumer_key
        self.token_secret = token_secret
        self.token = token

        # Initiate our crypto class to take care of
        # signing/header generation
        self.crypto = Crytpo()


    def request(self, url, data=None, **kwargs):
        import requests
        from oauth2 import Request as oauth_request

        if data is None and url.rsplit('/',1)[-1] == 'initiate': #Authorization flow
            # Generate OAuth headers and signed request
            headers = self.generate_headers(url, method="GET")
            print 'headers for auth flow: %s' % headers
            #print 'Data for'
            headers = {"Authorization": headers}

            request = requests.get(url, headers=headers)

            if str(request.status_code) != '200':
                raise Exception('Could not send xapi statement to LRS. Status: %s, Message: %s' % (request.status_code,request.content))

            return (request.status_code, request.content)

        elif data is None: # GET request to server, probably to access some resources

            params = kwargs.get('filters', None)

            #print 'PARAMS (connecter.request): %s' % params

            if params:
                headers = self.generate_headers(url, method="GET", extra_params=params)
            else:
                headers = self.generate_headers(url, method="GET")


            headers = {"Authorization": headers, "X-Experience-API-Version": "1.0.1"}

            request = requests.get(url, headers=headers, params=params)


            if str(request.status_code) != '200':
                raise Exception('Could not get xapi statements. Status: %s, Message: %s' % (request.status_code,request.content))

            return (request.status_code,request.content)

        else: # Sending data to server

            statement_jsn = json.loads(data)

            statement_id = statement_jsn['id']
            params = {'statementId':statement_id}

            #print 'type of data: %s' % type(data)

            #Generate OAuth headers and signed request with extra params for LRS statementId
            #which must be in params and not added to header.
            headers = self.generate_headers(url, method="PUT", extra_params=params)
            #print 'headers for statement transfer flow: %s' % headers
            headers = {"Authorization": headers, "X-Experience-API-Version": "1.0.1"}

            if isinstance(data,str): #sending one statement
                request = requests.put(url, params=params, headers=headers, data=data)

                return (request.status_code, request.content)
            elif isinstance(data,list):
                #send batch statements
                raise NotImplementedError

    # Generates OAuth headers and signs a request
    def generate_headers(self, url, method=None, extra_params=None):
        params = {}

        timestamp = int(time.time())
        nonce = self.crypto.create_nonce()
        sig_method = "HMAC-SHA1"

        params.update({'oauth_consumer_key':self.consumer_key})
        params.update({'oauth_timestamp':timestamp})
        params.update({'oauth_nonce':nonce})
        params.update({'oauth_signature_method':sig_method})

        # Add in extra params if they exist, right now we're only support 1 param (xapi filters)
        # TODO: Might have to handle multiple params
        # if extra_params and len(extra_params) == 1:
        #     # print 'EXTRA_PARAMS: %s' % extra_params
        #     params.update(extra_params)
        if extra_params and len(extra_params) > 0:
            params.update(extra_params)

        # We can tell this in Auth-flow request by considering token, token_secret, callback and the http method
        # GET requests without an access_token&secret and WITH a callback are auth requests
        if method == "GET" and not self.token and not self.token_secret and self.callback:
            params.update({'oauth_callback': self.callback})

        # if we have an access token, add it just incase
        # we also need our access_token
        if self.token:
            params.update({'oauth_token':self.token})
            # params.update({'oauth_token_secret':self.token_secret})

        # Get base string to encrypt for signed request
        http_base_sig = self.crypto.generate_base_string(url,params,method=method)

        # Sign the request and add to header
        signature = self.crypto.sign_request(http_base_sig,self.secret,token_secret=self.token_secret)
        params.update({'oauth_signature':signature})

        # In the OAuth spec, all oauth_* headers must be sorted, encoded, and "OAuth" at the front
        header = "OAuth "
        sorted_params = sorted(params.keys())

        encode = urllib.quote_plus

        for i in range(len(sorted_params)):
            header = header + str(sorted_params[i]) + "=\"" + encode(str(params[sorted_params[i]]), "") + "\""

            if i < len(sorted_params) - 1:
                header = header + ","

        # print 'header-------------- '
        # print header
        # Return the headers as a string
        return header

class Crytpo(object):


    """
    Make Nonce function borrowed from python-oauth2 package -- Thanks smarty pants'!
    """
    def create_nonce(self, length=8):
        import random
        """Generate pseudorandom number."""
        return ''.join([str(random.randint(0, 9)) for i in range(length)])

    # Sign request by crypting the base_string with HMAC-SHA1 method using consumer_secret/token_secret as key
    def sign_request(self, base_string, secret, token_secret=None):
        from hashlib import sha1
        import hmac
        import binascii

        key = secret+"&"

        if token_secret:
            key = key + "%s" % token_secret

        #print 'key: %s' % key

        hash = hmac.new(str(key), base_string, sha1)

        # Return ascii formatted signature in base64
        return binascii.b2a_base64(hash.digest())[:-1]

    def generate_base_string(self, url, params, method="GET"):
        #print "PARAMS: %s" % params
        encode = urllib.quote_plus
        basestring = method + "&" + encode(url) + "&"
        keys = sorted(params.keys())

        for i in range(len(keys)):

            if keys[i] == 'oauth_callback':
                basestring = basestring + encode(unicode(keys[i]), "") + encode("=") \
                    + encode(encode(params[keys[i]]), "")
            elif keys[i] == 'statementId':
                basestring = basestring + encode(unicode(keys[i]), "") + encode("=") \
                    + encode(str(self.get_param_value(params[keys[i]])), "")
            else:
                basestring = basestring + encode(unicode(keys[i]), "") + encode("=") \
                    + self.escape(encode(str(self.get_param_value(params[keys[i]])), ""))

            if i < len(keys) - 1:
                basestring = basestring + encode("&")

        return basestring.encode('ascii')


    def get_param_value(self, values):
        if not isinstance(values, list):
            return values

        return ','.join(values)

    @classmethod
    def escape(self, s):
        """Escape a URL including any /."""
        return urllib.quote(s, safe='~')
