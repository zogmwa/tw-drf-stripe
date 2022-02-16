import uuid
from django.db import models
from django.db.models import UniqueConstraint
from api.models.third_party_customer import ThirdPartyCustomer


class ThirdPartyCustomerSession(models.Model):
    """
    Third party customer session is for store the third party customer's session info.
    """

    third_party_customer = models.ForeignKey(
        ThirdPartyCustomer,
        on_delete=models.CASCADE,
    )

    session_id = models.UUIDField(default=uuid.uuid4, editable=False)

    expiration_time = models.DateTimeField(null=True, blank=True)

    is_expired = models.BooleanField(
        default=False,
        help_text='When payment action is finished then this value should be set to True.',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['session_id'], name='third_party_customer_session_id'
            )
        ]
        verbose_name = 'Third Party Customer Session'
        verbose_name_plural = 'Third Party Customer Sessions'
