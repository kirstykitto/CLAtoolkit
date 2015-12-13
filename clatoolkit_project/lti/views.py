from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response, redirect
from django.views.generic import View
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from dashboard.views import myclassifications
from django.template import RequestContext

from django.views.decorators.csrf import csrf_exempt
from ims_lti_py.tool_provider import ToolProvider, DjangoToolProvider
#from clatoolkit.forms import LTIProfileForm, LTIUserForm
from models import LTIProfile

import urllib2, json
#from lti.models import get_or_create_lti_user

"""def registerltiuser(request, params=None):
    if params is None:
        userform = LTIUserForm()
        ltiform = LTIProfileForm()

        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        role = request.POST.get('role', None)
        course_code = "MoodleTrial"

    else:

        params['userform'] = LTIUserForm()
        params['ltiform'] = LTIProfileForm()
        params['course_code'] = "MoodleTrial"
        return render_to_response('/register_via_lti.html', params
                                 )"""




class LTILaunch(View):

    http_method_names = ['post', 'get']

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(LTILaunch, self).dispatch(*args, **kwargs)

    def launch(self, req):
        if self.tool_provider.is_instructor():
            print 'REDIRECTING TO: "clatoolkit/dashboard/myclassifications.html/?course_code="moodletrial"&platform="Moodle"'
            return self.launch_instructor()
        elif self.tool_provider.is_student():
            return self.launch_student()

    def launch_student(self):

        return redirect('clatoolkit/dashboard/myclassifications.html/?course_code="moodletrial"&platform="Moodle"', permanent=True)


    def launch_instructor(self):
        #return myclassifications({'course_code':'moodletrial', 'platform':''})
        #return reverse('myclassifications')
        return redirect('/dashboard/myclassifications/?course_code=moodletrial&platform=Moodle&f=True', permanent=True)

    def setup_tool_provider(self, request):
        if 'oauth_consumer_key' not in request.POST:
            raise PermissionDenied()

        consumer_key = settings.LTI_KEY
        secret = settings.LTI_SECRET
        self.tool_provider = DjangoToolProvider(consumer_key, secret, request.POST)
        self.tool_provider.valid_request(request)

    def post(self, request, *args, **kwargs):
        if settings.LTI_DEBUG:
            for k,v in request.POST.items():
                print "{0} : {1}".format(k,v)

        self.setup_tool_provider(request)
        user = self.get_or_create_lti_user(self.tool_provider)
        login(request,user)
        return self.launch(request)

    def get(self, request, *args, **kwargs):
        if settings.LTI_DEBUG:
            for k,v in request.POST.items():
                print "{0} : {1}".format(k,v)

        return render_to_response('lti/lti_template.html')

    #LTI Helper Function
    def get_or_create_lti_user(self, tool_provider):
        #email = tool_provider.get_param('lis_person_contact_email_primary')
        #first_name = tool_provider.get_param('lis_person_name_full')
        #last_name = tool_provider.get_param('lis_person_name_full')
        #userid = tool_provider.get_param('user_id')

        params = tool_provider.to_params()


        username = None
        if params['lis_person_name_full'] is not None:
            username = "".join(params['lis_person_name_full'])

        params['username'] = username
        #last_name = None

        try:
            user = User.objects.get(username = username)

        except User.DoesNotExist:
            print 'creating a new user'
            email = params['lis_person_contact_email_primary'].rstrip('\x0e')
            userid = params['user_id']
            user = User.objects.create_user(username, email)

            #If user is only coming into toolkit via LMS, this will suffice
            user.set_unusable_password()


            #Set course code
            user.usersinunitoffering.add('6') #set to 6 until unit setup (for developmnet)


            LTIProfile.objects.create(user=user, institution_userid=userid)

        except User.MultipleObjectsReturned:
                print 'Multiple Users??'
        except Exception:
            print 'erorr....'

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()
        return user


def lti_auth(view):

    def _decorated_view(request, *args, **kwargs):
        if settings.LTI_DEBUG:
            for k,v in request.POST.items():
                print "{0} : {1}".format(k,v)

        if 'oauth_consumer_key' not in request.POST:
            raise PermissionDenied()

        consumer_key = settings.LTI_KEY
        secret =  settings.LTI_SECRET
        tp = DjangoToolProvider(consumer_key,secret,request.POST)
        tp.valid_request(request)

        user = get_or_create_lti_user(tp)
        login(request, user)
        return view(request, tp=tp)

    return _decorated_view

@lti_auth
def lti_view(request, tp=None):
    if tp is None:
        raise PermissionDenied()

    if tp.is_instructor():
        return NotImplementedError
    elif tp.is_student():
        return NotImplementedError



#Convienience method to create POST method for LTI registration
"""def create_register_post_method(url, data):
    #opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, json.dumps(data))
    request.add_header("Content-Type", "application/json") #header, value

    return redirect(url+'register_via_lti.html', request, permanent=True)"""