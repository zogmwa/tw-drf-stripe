from django.conf import settings
from django.db import models

from django.db.models import F
from api.models import Solution
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.signals import request_finished


class SolutionBooking(models.Model):
    """
    Used to represent individual Solution orders/bookings.
    """

    class Status(models.TextChoices):
        PENDING = 'Pending'
        IN_PROGRESS = 'In Progress'
        IN_REVIEW = 'In Review'
        COMPLETED = 'Completed'

    solution = models.ForeignKey(
        Solution,
        null=True,
        # If we delete a solution offering all bookings should not be lost
        on_delete=models.SET_NULL,
        related_name='bookings',
    )
    is_payment_completed = models.BooleanField(default=False)

    # Stripe Checkout Session Id associated with this payment. Can be null if it's not a checkout booking.
    stripe_session_id = models.CharField(null=True, blank=True, max_length=254)

    # The price the user paid at the time of the booking in case the offer price of the Solution changes later
    price_at_booking = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )

    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solution_bookings',
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_solution_bookings',
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Notes from the solution provider as the solution booking progresses along that will be visible to the customer
    provider_notes = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['booked_by'], name='booked_by_index'),
        ]


@receiver(pre_save, sender=SolutionBooking)
def count_update_for_new_or_complete_booking(sender, instance=None, **kwargs):
    """
    When new review is added, the `bookings_pending_fulfillment_count` is update with instance status.
    """

    if type(sender) != type(SolutionBooking):
        return

    try:
        # Update operation (an existing review is being updated case)
        # Try to get an old reference to this instance.
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance:
            if instance.status == sender.Status.COMPLETED:
                Solution.objects.filter(id=instance.solution.id).update(
                    bookings_pending_fulfillment_count=F(
                        'bookings_pending_fulfillment_count'
                    )
                    - 1,
                )
        else:
            if instance.status != sender.Status.COMPLETED:
                Solution.objects.filter(id=instance.solution.id).update(
                    bookings_pending_fulfillment_count=F(
                        'bookings_pending_fulfillment_count'
                    )
                    + 1,
                )

    except sender.DoesNotExist:
        # New solution booking is being added
        Solution.objects.filter(id=instance.solution.id).update(
            bookings_pending_fulfillment_count=F('bookings_pending_fulfillment_count')
            + 1,
        )


# https://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave
request_finished.connect(
    count_update_for_new_or_complete_booking,
    dispatch_uid="count_update_for_new_or_complete_booking",
)
