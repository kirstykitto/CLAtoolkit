from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, LearningRecord, UnitOffering, AccessLog, CachedContent, Classification, UserClassification

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'data integration user'

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

class LearningRecordAdmin(admin.ModelAdmin):
    list_display = ('username', 'platform', 'verb', 'course_code', 'platformid')
    search_fields = ('username', 'course_code')

class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('url', 'userid', 'created_at')
    search_fields = ('userid','url')

class UnitOfferingAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)

class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('xapistatement', 'classification', 'classifier', 'created_at')
    search_fields = ('classification',)

class UserClassificationAdmin(admin.ModelAdmin):
    list_display = ('classification', 'username', 'isclassificationcorrect', 'userreclassification', 'feedback', 'created_at')
    search_fields = ('username', 'isclassificationcorrect', 'userreclassification',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(LearningRecord, LearningRecordAdmin)

admin.site.register(UnitOffering, UnitOfferingAdmin)

admin.site.register(AccessLog, AccessLogAdmin)

admin.site.register(CachedContent)

admin.site.register(Classification, ClassificationAdmin)

admin.site.register(UserClassification, UserClassificationAdmin)
