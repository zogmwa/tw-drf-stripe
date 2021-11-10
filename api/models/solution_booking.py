from django.conf import settings
from django.db import models

from api.models import Solution


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
    )

    # The price the user paid at the time of the booking in case the offer price of the Solution changes later
    price_at_booking = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )

    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booked_solutions',
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_solutions',
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
