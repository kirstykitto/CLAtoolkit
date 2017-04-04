__author__ = 'zak'

"""
A django-nized implementation imspired by ADL prototypes' statement query object in javacript
"""
import requests

class Query(object):

    def __init__(self, filters):

        self.check_required_filters(filters)

        self.filters=filters

    def get(self):
        from xapi.oauth_consumer.operative import LRS_Auth

        session = requests.Session()
        r = requests.Request

        lrs = LRS_Auth()

    def check_required_filters(self, filters):
        _req_params = [
            'course_code',
            'registration',
            'id'
        ]

        filter_args = filters.keys()

        if not any(i in _req_params for i in filter_args):
            raise ValueError('Cannot Get statement')

        
        
        




