from django.db import models
from django.contrib.auth.models import User
from django_pgjson.fields import JsonField
import os

class UserProfile(models.Model):
    '''
    Custom user for data integration, uses Django's User class.
    '''
    user = models.OneToOneField(User)

    # Simple role as an alternative to django groups and permissions
    STAFF = 'Staff'
    STUDENT = 'Student'
    VISITOR = 'Visitor'
    ROLETYPE_OPTIONS = (
        (STAFF, STAFF),
        (STUDENT, STUDENT),
        (VISITOR, VISITOR)
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
    # YouTube 26/08/2015
    google_account_name = models.CharField(max_length=255, blank=True)

    #Diigo userName
    diigo_username = models.CharField(max_length=255, blank=True)

    #blog userName
    blog_id = models.CharField(max_length=255, blank=True)
    
    #GitHub user account
    github_account_name = models.CharField(max_length=255, blank=True)

    #Trello user ID
    trello_account_name = models.CharField(max_length=255, blank=True)

class UserTrelloCourseBoardMap(models.Model):
    user = models.ForeignKey(User)
    course_code = models.CharField(max_length=1000, blank=False)
    board_id = models.CharField(max_length=5000, blank=False)

class OfflinePlatformAuthToken(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=1000, blank=False)
    platform = models.CharField(max_length=1000, blank=False)

class OauthFlowTemp(models.Model):
    googleid = models.CharField(max_length=1000, blank=False)
    platform = models.CharField(max_length=1000, blank=True)
    course_code = models.CharField(max_length=1000, blank=True)
    transferdata = models.CharField(max_length=1000, blank=True)

class LearningRecord(models.Model):
    xapi = JsonField()
    course_code = models.CharField(max_length=5000, blank=False)
    platform = models.CharField(max_length=5000, blank=False)
    verb = models.CharField(max_length=5000, blank=False)
    username = models.CharField(max_length=5000, blank=True)
    platformid = models.CharField(max_length=5000, blank=True)
    platformparentid = models.CharField(max_length=5000, blank=True)
    parentusername = models.CharField(max_length=5000, blank=True)
    parentdisplayname = models.CharField(max_length=5000, blank=True)
    message = models.TextField(blank=True)
    #mentions = models.TextField(blank=True)
    datetimestamp = models.DateTimeField(blank=True, null=True)
    senttolrs = models.CharField(max_length=5000, blank=True)

class SocialRelationship(models.Model):
    course_code = models.CharField(max_length=5000, blank=False)
    platform = models.CharField(max_length=5000, blank=False)
    verb = models.CharField(max_length=5000, blank=False)
    fromusername = models.CharField(max_length=5000, blank=True)
    tousername = models.CharField(max_length=5000, blank=True)
    platformid = models.CharField(max_length=5000, blank=True)
    message = models.TextField(blank=False)
    datetimestamp = models.DateTimeField(blank=True)

class CachedContent(models.Model):
    htmltable = models.TextField(blank=False)
    activitytable = models.TextField(blank=True)
    course_code = models.CharField(max_length=5000, blank=False)
    platform = models.CharField(max_length=5000, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

class AccessLog(models.Model):
    url = models.CharField(max_length=10000, blank=False)
    userid = models.CharField(max_length=5000, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Classification(models.Model):
    xapistatement = models.ForeignKey(LearningRecord)
    classification = models.CharField(max_length=1000, blank=False)
    classifier = models.CharField(max_length=1000, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

class UserClassification(models.Model):
    classification = models.ForeignKey(Classification)
    username = models.CharField(max_length=5000, blank=False)
    isclassificationcorrect = models.BooleanField(blank=False)
    userreclassification = models.CharField(max_length=1000, blank=False)
    feedback = models.TextField(blank=True)
    feature = models.TextField(blank=True)
    trained = models.BooleanField(blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class UnitOffering(models.Model):
    code = models.CharField(max_length=5000, blank=False)
    name = models.CharField(max_length=5000, blank=False)

    #teaching periods
    SEM1 = 'Sem1'
    SEM2 = 'Sem2'
    SUM1 = 'Summer1'
    SUM2 = 'Summer2'
    SUM_ALL = 'Summer'
    #School of Business periods
    _6tp = ['6TP%s'%(num+1) for num in range(6)]
    _6TPN = dict(zip([(i+1) for i in range(len(_6tp))], _6tp))
    #English Language programs teaching periods
    _5tp = ['5TP%s'%(num+1) for num in range(9)]
    _5TPN = dict(zip([(i+1) for i in range(len(_5tp))], _5tp))
    #EAP program teaching periods
    _12tp = ['12TP%s'%(num+1) for num in range(3)]
    _12TPN = dict(zip([(i+1) for i in range(len(_12tp))], _12tp))
    #QUTIC courses/units periods
    _13tp = ['13TP%s'%(num+1) for num in range(3)]
    _13TPN = dict(zip([(i+1) for i in range(len(_13tp))], _13tp))
    XCH_1 = 'XCH-1'
    XCH_2 = 'XCH-2'
    R1 = 'R1'
    R2 = 'R2'

    TP_OPTIONS = (
        (SEM1, SEM1),
        (SEM2, SEM2),
        (SUM1, SUM1),
        (SUM_ALL, SUM_ALL),
        (_6TPN[1], _6TPN[1]),
        (_6TPN[2], _6TPN[2]),
        (_6TPN[3], _6TPN[3]),
        (_6TPN[4], _6TPN[4]),
        (_6TPN[5], _6TPN[5]),
        (_6TPN[6], _6TPN[6]),
        (_5TPN[1], _5TPN[1]),
        (_5TPN[2], _5TPN[2]),
        (_5TPN[3], _5TPN[3]),
        (_5TPN[4], _5TPN[4]),
        (_5TPN[5], _5TPN[5]),
        (_5TPN[6], _5TPN[6]),
        (_5TPN[7], _5TPN[7]),
        (_5TPN[8], _5TPN[8]),
        (_5TPN[9], _5TPN[9]),
        (_12TPN[1], _12TPN[1]),
        (_12TPN[2], _12TPN[2]),
        (_12TPN[3], _12TPN[3]),
        (_13TPN[1], _13TPN[1]),
        (_13TPN[2], _13TPN[2]),
        (_13TPN[3], _13TPN[3]),
        (XCH_1, XCH_1),
        (XCH_2, XCH_2),
        (R1, R1),
        (R2, R2)
    )

    semester = models.CharField(max_length=5000, choices=TP_OPTIONS, default=SEM2)

    description = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='usersinunitoffering')
    # determines whether unit should be displayed on Register form and on dashboard
    enabled = models.BooleanField(blank=False, default=False)
    # determines whether unit should be displayed on EventRegistration Form
    event = models.BooleanField(blank=False, default=False)
    # determines whether COI Classifier link should be diplayed for staff and student in a unit
    enable_coi_classifier = models.BooleanField(blank=True, default=False)

    # Twitter Unit Integration Requirements
    twitter_hashtags = models.TextField(blank=False)

    # Google Unit Integration Requirements
    google_groups = models.TextField(blank=True)

    # Facebook Unit Integration Requirements
    facebook_groups = models.TextField(blank=True)

    # Unit External Forums
    forum_urls = models.TextField(blank=True)

    # YouTube 26/08/2015
    youtube_channelIds = models.TextField(blank=True)

    # Diigo Tags
    diigo_tags = models.TextField(blank=True)

    # Blog Members (for blogrss plugin)
    blogmember_urls = models.TextField(blank=True)

    # GitHub Repository URLs
    github_urls = models.TextField(blank=True)

    # Trello board IDs 15/07/16
    attached_trello_boards = models.TextField(blank=True)

    # Determines which platforms should be utilized by COI classifier
    coi_platforms = models.TextField(blank=True)


    # LRS Integration - to send users data to unit LRS
    ll_endpoint = models.CharField(max_length=60, blank=True)
    ll_username = models.CharField(max_length=60, blank=True)
    ll_password = models.CharField(max_length=60, blank=True)

    def __unicode__(self):
        return self.code + " " + self.name

    def trello_boards_as_list(self):
        if self.attached_trello_boards:
            return self.attached_trello_boards.split(',')
        else:
            return []

    def twitter_hashtags_as_list(self):
        if self.twitter_hashtags:
            return self.twitter_hashtags.split(',')
        else:
            return []

    def facebook_groups_as_list(self):
        if self.facebook_groups:
            return self.facebook_groups.split(',')
        else:
            return []

    def forum_urls_as_list(self):
        if self.forum_urls:
            return self.forum_urls.split(',')
        else:
            return []

    def youtube_channelIds_as_list(self):
        if self.youtube_channelIds:
            return self.youtube_channelIds.split(',')
        else:
            return []

    def diigo_tags_as_list(self):
        if self.diigo_tags:
            return self.diigo_tags.split(',')
        else:
            return []

    def blogmember_urls_as_list(self):
        if self.blogmember_urls:
            return self.blogmember_urls.split(',')
        else:
            return []

    def github_urls_as_list(self):
        if self.github_urls:
            return self.github_urls.split(os.linesep)
        else:
            return []

    def coi_platforms_as_list(self):
        if self.coi_platforms:
            return self.coi_platforms.split(',')
        else:
            return []

    def get_required_platforms(self):
        platforms = []

        if len(self.twitter_hashtags_as_list()):
            platforms.append('twitter')
        if len(self.facebook_groups_as_list()):
            platforms.append('facebook')
        if len(self.forum_urls_as_list()):
            platforms.append('forum')
        if len(self.youtube_channelIds_as_list()):
            platforms.append('youtube')
        if len(self.diigo_tags_as_list()):
            platforms.append('diigo')
        if len(self.blogmember_urls_as_list()):
            platforms.append('blog')
        if len(self.github_urls_as_list()):
            platforms.append('github')
        if len(self.trello_boards_as_list()):
            platforms.append('trello')

        return platforms

class ApiCredentials(models.Model):
    platform_uid = models.CharField(max_length=5000, blank=False)
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

class GroupMap(models.Model):
    userId = models.ForeignKey(User)
    course_code = models.CharField(max_length=5000, blank=False)
    groupId = models.IntegerField(blank=False)
