from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint

from api.models import Asset


class AssetReview(models.Model):
    RATING_RANGE = range(1, 11)    # 1 to 10 (11 excluded)
    RATING_CHOICES = tuple(zip(RATING_RANGE, map(str, RATING_RANGE)))

    asset = models.ForeignKey(Asset, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        related_name='reviews',
        # SET_NULL because we want to retain a review even if the corresponding user is deleted
        on_delete=models.SET_NULL,
    )
    content = models.TextField(max_length=1024, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}: {}".format(self.asset, self.user, self.rating)

    class Meta:
        # One user should not be able to vote on the same asset/web-service more than once
        constraints = [
            UniqueConstraint(fields=['asset', 'user'], name='user_asset_review')
        ]

        verbose_name = 'Web Service Review'
        verbose_name_plural = 'Web Service Reviews'
