from django.db import models
from django.contrib.auth.models import User
from django_pgjson.fields import JsonField

class UserProfile(models.Model):
    '''
    Custom user for data integration, uses Django's User class.
    '''
    user = models.OneToOneField(User)

    # Simple role as an alternative to django groups and permissions
    STAFF = 'Staff'
    STUDENT = 'Student'
    ROLETYPE_OPTIONS = (
        (STAFF, STAFF),
        (STUDENT, STUDENT)
    )
    role = models.CharField(max_length=100, choices=ROLETYPE_OPTIONS, default=STUDENT)

    # LRS Integration - to send users data to personal LRS
    #ll_endpoint = models.CharField(max_length=60)
    #ll_username = models.CharField(max_length=60)
    #ll_password = models.CharField(max_length=60)

    # Facebook Integration - users facebook id is required
    fb_id = models.CharField(max_length=30, blank=True)

    # Twitter Integration - users Twitter handle (username) is required
    twitter_id = models.CharField(max_length=30, blank=True)

    # Forum Scraping - users Forum handle (username) is required
    forum_id = models.CharField(max_length=500, blank=True)

    # Google Integration - users Google xxx is required for Youtube, etc...
    # Todo - Add Google API user credential requirements below

class LearningRecord(models.Model):
    xapi = JsonField()
    course_code = models.CharField(max_length=5000, blank=False)
    platform = models.CharField(max_length=5000, blank=False)
    verb = models.CharField(max_length=5000, blank=False)
    username = models.CharField(max_length=5000, blank=True)

class UnitOffering(models.Model):
    code = models.CharField(max_length=5000, blank=False)
    name = models.CharField(max_length=5000, blank=False)
    semester = models.CharField(max_length=5000, blank=False)
    description = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='usersinunitoffering')
    # determines whether unit should be displayed on Register form and on dashboard
    enabled = models.BooleanField(blank=False, default=False)
    # determines whether unit should be displayed on EventRegistration Form
    event = models.BooleanField(blank=False, default=False)

    # Twitter Unit Integration Requirements
    twitter_hashtags = models.TextField(blank=False)

    # Google Unit Integration Requirements
    google_groups = models.TextField(blank=True)

    # Facebook Unit Integration Requirements
    facebook_groups = models.TextField(blank=True)

    # Unit External Forums
    forum_urls = models.TextField(blank=True)

    # LRS Integration - to send users data to unit LRS
    ll_endpoint = models.CharField(max_length=60, blank=True)
    ll_username = models.CharField(max_length=60, blank=True)
    ll_password = models.CharField(max_length=60, blank=True)

    def __unicode__(self):
        return self.code + " " + self.name

class ApiCredentials(models.Model):
    platform = models.CharField(max_length=5000, blank=False)
    credentials_json = JsonField()

class DashboardReflection(models.Model):
    username = models.CharField(max_length=5000, blank=False)
    strategy = models.TextField(blank=False)

    HAPPY = 'Happy'
    SATISFIED = 'Satisfied'
    UNHAPPY = 'Unhappy'
    RATING_OPTIONS = (
        (HAPPY, HAPPY),
        (SATISFIED, SATISFIED),
        (UNHAPPY, UNHAPPY)
    )
    rating = models.CharField(max_length=50, choices=RATING_OPTIONS, default=SATISFIED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id + ": " + self.username
