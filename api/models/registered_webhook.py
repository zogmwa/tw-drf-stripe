from django.db import models
from django.db.models import UniqueConstraint
from api.models.organization import Organization


class RegisteredWebhook(models.Model):
    """
    A partner could be request webhook event.
    """

    # webhook event type
    EVENT_CHOICES = [
        ('payment_method.attach', 'payment_method.attach'),
        ('payment_method.detach', 'payment_method.detach'),
    ]
    event_name = models.CharField(max_length=21, choices=EVENT_CHOICES)

    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    # partner's webhook receive url
    receiver_url = models.URLField(max_length=2048, null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['event_name', 'organization'], name='registered_webhook'
            )
        ]
