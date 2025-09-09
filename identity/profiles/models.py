from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150)
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

class Friendship(models.Model):
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='requests_sent', on_delete=models.CASCADE)
    addressee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('requested','requested'),('accepted','accepted'),('blocked','blocked')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('requester', 'addressee')
