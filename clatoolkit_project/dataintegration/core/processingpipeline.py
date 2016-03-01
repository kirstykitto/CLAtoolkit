from clatoolkit.models import CachedContent
from dashboard.utils import *

def post_smimport(course_code, platform):
        top_content = get_top_content_table(platform, course_code)
        active_content = get_active_members_table(platform, course_code)
        cached_content, created = CachedContent.objects.get_or_create(course_code=course_code, platform=platform)
        cached_content.htmltable = top_content
        cached_content.activitytable = active_content
        cached_content.save()

        #perform sentiment classification
        sentiment_classifier(course_code)
