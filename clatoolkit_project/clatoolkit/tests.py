from django.test import TestCase, Client
from lti.models import LTIProfile, get_or_create_lti_user
# Create your tests here.
class LTITest(TestCase):
    def setUp(self):
        c = Client()
        req = c.post('/lti_o/')