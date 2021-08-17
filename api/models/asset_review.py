from django.conf import settings
from django.db import models

from api.models import Asset


class AssetReview(models.Model):
    review_range = range(1, 11)    # 1 to 10 (11 excluded)
    RATING_CHOICES = tuple(zip(review_range, map(str, review_range)))

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
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
