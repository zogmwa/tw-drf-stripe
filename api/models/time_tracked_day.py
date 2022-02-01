from django.db import models
from django.db.models import UniqueConstraint
from api.models.user import User
from api.models.solution_booking import SolutionBooking


class TimeTrackedDay(models.Model):
    """
    This model is for storing the tracked times instances.
    """

    solution_booking = models.ForeignKey(
        SolutionBooking, null=True, on_delete=models.CASCADE
    )

    # Who is submitting these hours (It could be on behalf of the provider)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    date = models.DateTimeField(null=True)
    tracked_hours = models.DecimalField(null=True, max_digits=2, decimal_places=1)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['solution_booking', 'date'], name='booking_tracked_date'
            )
        ]

        verbose_name = 'Time Tracked Day'
        verbose_name_plural = 'Time Tracked Days'
