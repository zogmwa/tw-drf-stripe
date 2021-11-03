from django.conf import settings
from django.db import models

from api.models.organization import Organization


class Solution(models.Model):
    """
    A solution can be an integration support/solution, usage support, or some other form solution/support
    related to one or more web service(s), which is provided by a specific organization or a user.
    """

    title = models.CharField(max_length=255)
    detailed_description = models.TextField(blank=True, null=True)
    scope_of_work = models.TextField(blank=True, null=True)

    class Type(models.TextChoices):
        INTEGRATION = 'I'
        USAGE_SUPPORT = 'U'

    type = models.CharField(
        max_length=2, choices=Type.choices, default=Type.INTEGRATION
    )

    # There may or may not be an organization providing this solution (in that case point_of_contact user will be
    # providing the support)
    organization = models.ForeignKey(
        Organization, blank=True, null=True, on_delete=models.SET_NULL
    )

    # The user who will either be providing the support or be the point of contact at the organization providing
    # the support.
    point_of_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    # Estimated number of days it will take to fully deliver the solution to the customer
    eta_days = models.IntegerField(null=True, blank=True)

    # If the price is None that doesn't mean it is 0, it's just that we don't know that yet and this specific
    # solution requires the solution provider to send the user a quote. This will be more of an estimated price
    # and not an actual price.
    price = models.DecimalField(null=True, blank=True, max_digits=7, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # https://hackernoon.com/why-capacity-planning-needs-queueing-theory-without-the-hard-math-342a851e215c
    # Max number of active solution bookings that the team can handle at any given time for this solution.
    # This is used so that we may prevent overbooking of solutions.
    capacity = models.IntegerField(default=10)

    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Micro Solution'
        verbose_name_plural = 'Micro Solutions'


class SolutionBooking(models.Model):
    """
    Used to represent individual Solution orders/bookings.
    """

    class Status(models.TextChoices):
        PENDING = 'Pending'
        IN_PROGRESS = 'In Progress'
        IN_REVIEW = 'In Review'
        COMPLETED = 'Completed'

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
