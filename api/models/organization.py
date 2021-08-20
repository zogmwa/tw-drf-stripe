from django.db import models


class Organization(models.Model):
    """
    A Organization could be the owner of multiple assets (only one organization per asset).
    """
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(max_length=2048, null=True, blank=True)

    def __str__(self):
        return self.name
