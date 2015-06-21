from django import forms


class TwitterGatherForm(forms.Form):
    account = forms.CharField(label='Account', max_length=50)
    hashtag = forms.CharField(label='Hashtag', max_length=100)
