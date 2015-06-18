__author__ = 'James'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile

# class DataIntegrationUserAdmin(admin.ModelAdmin):
#     list_display = ['name', 'email', 'fb_id', 'll_endpoint', 'll_username', 'll_password']
#     list_filter = ['name', 'email', 'fb_id', 'll_endpoint', 'll_username', 'll_password']
#
#
# admin.site.register(DataIntegrationUser, DataIntegrationUserAdmin)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'data integration user'

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)