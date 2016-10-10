from clatoolkit.models import CachedContent
from dashboard.utils import *


def post_smimport(unit, platform):
        top_content = get_top_content_table(unit, platform)
        active_content = get_active_members_table(unit, platform)
        cached_content, created = CachedContent.objects.get_or_create(unit=unit, platform=platform)
        cached_content.htmltable = top_content
        cached_content.activitytable = active_content
        cached_content.save()

        #perform sentiment classification
        sentiment_classifier(unit)
