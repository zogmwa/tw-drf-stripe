from django.db import models

from api.models import Tag, Asset


class LinkedTag(models.Model):
    """
    M2M Model that links tags with an assets
    """
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
