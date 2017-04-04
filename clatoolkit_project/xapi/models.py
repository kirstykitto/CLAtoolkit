from django.db import models
from django.contrib.auth.models import User

class ClientApp(models.Model):
    provider = models.CharField(max_length=256, unique=True)
    app_name = models.CharField(max_length=256, blank=False)
    i = models.CharField(max_length=256, blank=False)
    s = models.CharField(max_length=256, blank=False)
    protocol = models.CharField(max_length=10, blank=False)
    domain = models.CharField(max_length=256, blank=False)
    port = models.CharField(max_length=6, blank=False)
    auth_request_path = models.CharField(max_length=256, blank=False)
    access_token_path = models.CharField(max_length=256, blank=False)
    authorization_path = models.CharField(max_length=256, blank=False)
    xapi_statement_path = models.CharField(max_length=256, blank=False)
    reg_lrs_account_path = models.CharField(max_length=256, blank=False)

    def get_key(self):
        return self.i

    def get_secret(self):
        return self.s

    def get_base_url(self):
        return '%s://%s:%s' % (self.protocol, self.domain, str(self.port))

    def get_auth_request_url(self):
        return self.get_base_url() + self.auth_request_path

    def get_access_token_url(self):
        return self.get_base_url() + self.access_token_path

    def get_authorization_url(self):
        return self.get_base_url() + self.authorization_path

    def get_xapi_statement_url(self):
        return self.get_base_url() + self.xapi_statement_path

    def get_reg_lrs_account_url(self):
        return self.get_base_url() + self.reg_lrs_account_path


class UserAccessToken_LRS(models.Model):
    user = models.ForeignKey(User)
    access_token = models.CharField(max_length=256, blank=False)
    access_token_secret = models.CharField(max_length=256, blank=False)
    clientapp = models.ForeignKey(ClientApp)

# Create your models here.
class OAuthTempRequestToken(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=256, blank=False)
    secret = models.CharField(max_length=256, blank=False)
    clientapp = models.ForeignKey(ClientApp)
