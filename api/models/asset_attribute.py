from django.db import models
from django.db.models import UniqueConstraint
from django.conf import settings

from .asset import Asset


class Attribute(models.Model):
    """
    An asset attribute is something that describes an asset like 'Easy to Use'. It's different from a tag
    in that rather than being a category tag it is kind of like a feature or highlight that
    acts as an adjective for the web service it is used on.
    """
    name = models.CharField(max_length=55, unique=True)

    # Default it is a positive attribute/pro, unless it's marked as a con/negative
    is_con = models.BooleanField(default=False)

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Web Service Attribute'
        verbose_name_plural = 'Web Service Attributes'


class LinkedAttribute(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)


class AttributeVote(models.Model):
    """
    A vote on a specific attribute on a specific asset (only one vote per user per attribute per asset).
    """
    is_upvote = models.BooleanField(default=True, help_text='Whether this is an Upvote=true (or Downvote=false)')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='attribute_votes',
        on_delete=models.CASCADE,
    )
    attribute = models.ForeignKey(Attribute, related_name='attribute_votes', on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, related_name='attribute_votes', on_delete=models.CASCADE)
    voted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}: {}".format(self.attribute, self.user)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'asset', 'attribute'], name='user_asset_attribute_vote')
        ]
        verbose_name = 'Web Service Attribute Vote'
        verbose_name_plural = 'Web Service Attribute Votes'
