from django import template
from clatoolkit.models import AccessLog

register = template.Library()

# log tag
@register.simple_tag
def accesslog(userid,url):
    entry = AccessLog(url=url, userid=userid)
    entry.save()
