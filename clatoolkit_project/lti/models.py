from django.db import models
from clatoolkit.models import UserProfile
import hashlib

from django.contrib.auth.models import User
from ims_lti_py.utils import InvalidLTIRequestError

#Model for LTI Integration
class LTIProfile(models.Model):
    """LTI User profile. Can be retrieved by calling get_profile() on the User model"""

    user = models.OneToOneField(User, null=True)
    #roles = models.CharField(max_length=255, blank=True, null=True)
    institution_userid = models.CharField(max_length=255)
    #loggedin = models.BooleanField(blank=False, default=False)
    ethics_agreement = models.BooleanField(blank=False, default=False)

    def __unicode__(self):
        return self.user.username

