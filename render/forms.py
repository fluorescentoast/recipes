from django.forms import ModelForm
from django import forms
from .models import YouTubeModel

class YouTubeForm(ModelForm):
    youtube_url = forms.TextInput()

    class Meta:
        model = YouTubeModel
        fields = ['youtube_url']