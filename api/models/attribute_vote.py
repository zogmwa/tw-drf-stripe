from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint

from api.models import Attribute, Asset


class AttributeVote(models.Model):
    """
    A vote on a specific attribute on a specific asset (only one vote per user per attribute per asset).
    """

    is_upvote = models.BooleanField(
        default=True, help_text='Whether this is an Upvote=true (or Downvote=false)'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='attribute_votes',
        on_delete=models.CASCADE,
    )
    attribute = models.ForeignKey(
        Attribute, related_name='attribute_votes', on_delete=models.CASCADE
    )
    asset = models.ForeignKey(
        Asset, related_name='attribute_votes', on_delete=models.CASCADE
    )
    voted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}: {}".format(self.attribute, self.user)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'asset', 'attribute'], name='user_asset_attribute_vote'
            )
        ]
        verbose_name = 'Web Service Attribute Vote'
        verbose_name_plural = 'Web Service Attribute Votes'
