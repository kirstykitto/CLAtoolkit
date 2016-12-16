from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class OAuthTempRequestToken(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=256, blank=False)
    secret = models.CharField(max_length=256, blank=False)

class UserAccessToken_LRS(models.Model):
    user = models.ForeignKey(User)
    access_token = models.CharField(max_length=256, blank=False)
    access_token_secret = models.CharField(max_length=256, blank=False)

class ClientApp(models.Model):
    provider = models.CharField(max_length=256, unique=True)
    i = models.CharField(max_length=256, blank=False)
    s = models.CharField(max_length=256, blank=False)
    protocol = models.CharField(max_length=10, blank=False)
    domain = models.CharField(max_length=256, blank=False)
    port = models.CharField(max_length=6, blank=False)
    auth_request_path = models.CharField(max_length=256, blank=False)
    access_token_path = models.CharField(max_length=256, blank=False)
    authorization_path = models.CharField(max_length=256, blank=False)
    xapi_statement_path = models.CharField(max_length=256, blank=False)

    def get_key(self):
        return self.i

    def get_secret(self):
        return self.s