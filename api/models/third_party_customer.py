from django.db import models
from django.db.models import UniqueConstraint

from api.models import Organization
from djstripe.models import Customer as StripeCustomer


class ThirdPartyCustomer(models.Model):
    """
    A model to hold data of customers of different organizations i.e. these customers are not directly our customers but
    belong to a different organization we partner with to process payments.
    """

    customer_uid = models.CharField(max_length=255)  # partner provided customer uid

    stripe_customer = models.OneToOneField(
        StripeCustomer,
        null=True,
        blank=True,
        related_name='organizations',
        on_delete=models.SET_NULL,
    )

    # This should be set using the API key of the user making the request to our API.
    # E.g. If thecodemesh_user is making the request then organization = thecodemesh_user.organization
    organization = models.ForeignKey(Organization, on_delete=models.RESTRICT)

    # In case the customer is also logged in on our end we may want this field as well but we can always add it later, not needed in the beginning
    # taggedweb_user = FK(settings.AUTH_USER_MODEL, null=True, blank=True)

    @property
    def customer_email(self):
        return self.stripe_customer.email

    class Meta:
        verbose_name = 'Third Party Customer'
        verbose_name_plural = 'Third Party Customers'

        constraints = [
            UniqueConstraint(
                fields=['customer_uid', 'organization'],
                name='third_party_organization_customer',
            )
        ]
