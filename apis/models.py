from django.db import models


# Create your models here.
class NewsArticlePublishTime(models.Model):
    source = models.TextField(primary_key=True)
    timestamp = models.DateTimeField()
    log = models.TextField(blank=True, null=True)
