from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint, F
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.signals import request_finished
from api.utils.video_url_conditional_updates_signal import video_url_conditional_updates

from api.models import Asset


class AssetReview(models.Model):
    RATING_RANGE = range(1, 11)  # 1 to 10 (11 excluded)
    RATING_CHOICES = tuple(zip(RATING_RANGE, map(str, RATING_RANGE)))

    asset = models.ForeignKey(Asset, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='reviews',
        # SET_NULL because we want to retain a review even if the corresponding user is deleted
        on_delete=models.SET_NULL,
    )
    content = models.TextField(max_length=1024, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    video_url = models.URLField(max_length=2048, null=True, blank=True)

    def __str__(self):
        return "{}: {}: {}".format(self.asset, self.user, self.rating)

    class Meta:
        # One user should not be able to vote on the same asset/web-service more than once
        constraints = [
            UniqueConstraint(fields=['asset', 'user'], name='user_asset_review')
        ]

        verbose_name = 'Software Review'
        verbose_name_plural = 'Software Reviews'


@receiver(pre_save, sender=AssetReview)
def avg_rating_and_count_update_for_new_review(sender, instance=None, **kwargs):
    """
    When new review is added, the average rating of the asset is recalculated & 'avg_rating' and 'reviews_count'
    for the asset is updated
    """

    if type(sender) != type(AssetReview):
        return

    try:
        # Update operation (an existing review is being updated case)
        # Try to get an old reference to this instance.
        instance_old = sender.objects.get(pk=instance.pk)
        if instance_old.rating != instance.rating:
            Asset.objects.filter(id=instance.asset_id).update(
                avg_rating=(
                    F('avg_rating') * F('reviews_count')
                    - instance_old.rating
                    + instance.rating
                )
                / (F('reviews_count')),
                reviews_count=F('reviews_count'),
            )

    except sender.DoesNotExist:
        # New review is being added
        Asset.objects.filter(id=instance.asset_id).update(
            avg_rating=(F('avg_rating') * F('reviews_count') + instance.rating)
            / (F('reviews_count') + 1),
            reviews_count=F('reviews_count') + 1,
        )


@receiver(post_delete, sender=AssetReview)
def avg_rating_and_count_update_on_delete(sender, instance=None, **kwargs):
    asset_qs = Asset.objects.filter(id=instance.asset_id)
    if asset_qs[0].reviews_count == 1:
        asset_qs.update(
            avg_rating=0,
            reviews_count=0,
        )
    else:
        asset_qs.update(
            avg_rating=(F('avg_rating') * F('reviews_count') - instance.rating)
            / (F('reviews_count') - 1),
            reviews_count=F('reviews_count') - 1,
        )


pre_save.connect(video_url_conditional_updates, sender=AssetReview)

# https://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave
request_finished.connect(
    avg_rating_and_count_update_for_new_review,
    dispatch_uid="avg_rating_and_count_update_for_new_review",
)
