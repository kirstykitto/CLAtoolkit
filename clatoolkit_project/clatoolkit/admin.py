from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, LearningRecord, UnitOffering, SocialRelationship, AccessLog, CachedContent, Classification, UserClassification, GroupMap

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'data integration user'

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# TODO - Fix admin
class LearningRecordAdmin(admin.ModelAdmin):
    pass
    # list_display = ('user', 'platform', 'verb', 'unit', 'platformid')
    # search_fields = ('user', 'unit', 'verb', 'platform')


# TODO - Fix admin
class SocialRelationshipAdmin(admin.ModelAdmin):
    pass
    # list_display = ('fromusername', 'tousername', 'platform', 'verb', 'course_code', 'platformid')
    # search_fields = ('verb', 'platform')

class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('url', 'userid', 'created_at')
    search_fields = ('userid','url')

class UnitOfferingAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)

class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('xapistatement', 'classification', 'classifier', 'created_at')
    search_fields = ('classification',)

class GroupMapAdmin(admin.ModelAdmin):
    list_display = ('userId', 'course_code', 'groupId')
    search_fields = ('course_code',)

class UserClassificationAdmin(admin.ModelAdmin):
    list_display = ('classification', 'username', 'isclassificationcorrect', 'userreclassification', 'feedback', 'created_at')
    search_fields = ('username', 'isclassificationcorrect', 'userreclassification',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(LearningRecord, LearningRecordAdmin)

admin.site.register(SocialRelationship, SocialRelationshipAdmin)

admin.site.register(UnitOffering, UnitOfferingAdmin)

admin.site.register(AccessLog, AccessLogAdmin)

admin.site.register(CachedContent)

admin.site.register(Classification, ClassificationAdmin)

admin.site.register(UserClassification, UserClassificationAdmin)

admin.site.register(GroupMap, GroupMapAdmin)
