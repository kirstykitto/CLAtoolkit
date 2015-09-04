from django import forms
from django.contrib.auth.models import User

from clatoolkit.models import UserProfile, UnitOffering

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
    class Meta:
        model = UserProfile
        fields = ('fb_id', 'twitter_id', 'forum_id')
