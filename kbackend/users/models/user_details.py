from django.db import models
from django.conf import settings


class UserDetails(models.Model):
    """ Additional user info that won't be queried frequently and should not clutter the User model """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    biography = models.TextField(max_length=2048, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
