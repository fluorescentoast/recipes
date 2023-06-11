from django.db import models

# Create your models here.
class YouTubeModel(models.Model):
    youtube_url = models.CharField(max_length=500)