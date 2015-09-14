from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, LearningRecord, UnitOffering, AccessLog, CachedContent

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'data integration user'

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

class LearningRecordAdmin(admin.ModelAdmin):
    list_display = ('username', 'platform', 'verb', 'course_code', 'platformid')
    search_fields = ('username', 'course_code')

class UnitOfferingAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(LearningRecord, LearningRecordAdmin)

admin.site.register(UnitOffering, UnitOfferingAdmin)

admin.site.register(AccessLog)

admin.site.register(CachedContent)
