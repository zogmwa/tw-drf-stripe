from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
from django.db.models.signals import pre_save
from django.dispatch import receiver

from api.models import Asset


class ClaimAsset(models.Model):
    asset = models.ForeignKey(
        Asset, related_name='claim_requests', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='claim_requests',
        on_delete=models.CASCADE,
    )
    STATUS_CHOICES = [
        ('Accepted', 'Accepted'),
        ('Denied', 'Denied'),
        ('Pending', 'Pending'),
    ]
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Pending')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['asset', 'user'], name='user_asset_claim_request')
        ]
        verbose_name = 'Web Service Claim Request'
        verbose_name_plural = 'Web Service Claim Requests'


@receiver(pre_save, sender=ClaimAsset)
def set_owner_of_asset_if_claim_asset_request_is_accepted(
    sender, instance=None, **kwargs
):
    """
    If the asset claim request of the user is accepted by admin/staff user, the ownership of the asset should be given
    to the user.
    """
    if instance.status == 'Accepted':
        Asset.objects.filter(id=instance.asset.id).update(owner=instance.user)
