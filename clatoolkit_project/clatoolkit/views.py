from django.shortcuts import render_to_response
from django.shortcuts import redirect

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django.contrib.auth.models import User

from django.template import RequestContext

# from fb_data.models import

def userlogin(request):
    context = RequestContext(request)

    if request.method == 'POST':
        print "posted"
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                print "sending to myunits"
                return HttpResponseRedirect('/dashboard/myunits/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your CLAToolkit account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            #print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        print "ordinary get"
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('clatoolkit/login.html', {}, context)
