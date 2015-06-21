# example/simple/views.py
from __future__ import absolute_import

from django.http import HttpResponse
from django.shortcuts import render

from tw_data.tasks import send_twitter_data_to_lrs
from .forms import TwitterGatherForm


def home(request):
    """
    Index for Twitter gathering app.
    Displays form to take account and hashtag for gathering.
    :param request: HTTP request
    :return: Gathering form.
    """
    form = TwitterGatherForm()
    return render(request, 'tw_data/twitter.html', {'form': form})


def twitter(request, account, sent_hashtag):
    """
    View that initiates data gathering.
    :param request: HTTP request
    :param account: Account to gather from.
    :param sent_hashtag: Hashtag to gather from.
    :return: Output from gathering.
    """
    hashtag = str(sent_hashtag)
    result = send_twitter_data_to_lrs.delay(account, sent_hashtag)
    html_response = HttpResponse()
    html_response.write('<p>Data is being collected from the username: ' + account + ' and hashtag: ' + hashtag)
    html_response.write('<p>View your task status <a href="http://localhost:5555/'
                        'task/' + result.id + '">here.</a></p>')
    return html_response
