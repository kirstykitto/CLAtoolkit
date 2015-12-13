from django.test import TestCase

import urllib2
import json

# Create your tests here.
class LTITestCase(TestCase):
    LTI_POST_data = {
        'lti_message_type' : 'basic-lti-launch-request',
        'lti_version' : 'LTI-1p0',

        'oauth_consumer_key' : 'cladevelopment01',
        'user_id' : '1212',

        'lis_person_name_full' : 'Zak Waters',
        'roles' : 'Learner'
    }

    url = "http://localhost:8000/lti/launch"
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(url, data=json.dumps(LTI_POST_data))
    req.add_header("Content-Type", "application/json")
    opener.open(req)