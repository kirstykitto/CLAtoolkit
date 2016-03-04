from django import forms
from django.contrib.auth.models import User
import django_filters
from django.core.exceptions import ValidationError
from clatoolkit.models import UserProfile, UnitOffering, LearningRecord, SocialRelationship, Classification, UserClassification

class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    units = forms.ModelMultipleChoiceField(queryset=UnitOffering.objects.filter(enabled=True), widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'units')

class UserProfileForm(forms.ModelForm):
    fb_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    twitter_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    forum_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    google_account_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    diigo_username = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        if not ((self.cleaned_data.get('fb_id')) or (self.cleaned_data.get('twitter_id')) or (self.cleaned_data.get('forum_id')) or (self.cleaned_data.get('google_account_name')) or or (self.cleaned_data.get('diigo_username'))):
            raise ValidationError("At least one social media account must be added.")

        return self.cleaned_data

    class Meta:
        model = UserProfile
        fields = ('fb_id', 'twitter_id', 'forum_id', 'google_account_name', 'diigo_username')

class LearningRecordFilter(django_filters.FilterSet):
    datetimestamp_min = django_filters.DateFilter(name='datetimestamp', lookup_type='gte')
    datetimestamp_max = django_filters.DateFilter(name='datetimestamp', lookup_type='lte')

    class Meta:
        model = LearningRecord
        fields = ('id', 'course_code', 'platform', 'verb', 'username', 'platformid', 'platformparentid', 'parentusername', 'message', 'datetimestamp', 'senttolrs', 'datetimestamp_min', 'datetimestamp_max')

class SocialRelationshipFilter(django_filters.FilterSet):
    datetimestamp_min = django_filters.DateFilter(name='datetimestamp', lookup_type='gte')
    datetimestamp_max = django_filters.DateFilter(name='datetimestamp', lookup_type='lte')

    class Meta:
        model = SocialRelationship
        fields = ('id', 'course_code', 'platform', 'verb', 'fromusername', 'tousername', 'platformid', 'message', 'datetimestamp', 'datetimestamp_min', 'datetimestamp_max')

class ClassificationFilter(django_filters.FilterSet):

    class Meta:
        model = Classification
        fields = ('id', 'xapistatement', 'classification', 'classifier')

class UserClassificationFilter(django_filters.FilterSet):

    class Meta:
        model = UserClassification
        fields = ('id', 'classification', 'username', 'isclassificationcorrect', 'userreclassification', 'feedback', 'feature')
