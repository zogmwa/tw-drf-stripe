from django.conf import settings
from django.db import models
from django.core.mail import send_mail

from django.db.models import F
import datetime
from api.utils.convert_str_to_date import get_now_converted_google_date
from api.models import Solution
from django.db.models.signals import pre_save, post_save, post_delete
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

    BOOKING_RATING_RANGE = range(-1, 2)  # -1, 0, 1 (2 excluded)
    BOOKING_RATING_CHOICES = tuple(
        zip(BOOKING_RATING_RANGE, map(str, BOOKING_RATING_RANGE))
    )

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

    # The timestamp that created when solution booking status from pending to some other status.
    started_at = models.DateTimeField(null=True, blank=True)

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

    # We should have rating at the booking level that the paying customer will add
    # sad, neutral or happy face (-1, 0, 1 respectively)
    rating = models.IntegerField(choices=BOOKING_RATING_CHOICES, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['booked_by'], name='booked_by_index'),
        ]
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'


@receiver(pre_save, sender=SolutionBooking)
def count_update_for_new_or_complete_booking(sender, instance=None, **kwargs):
    """
    When new review is added, the `bookings_pending_fulfillment_count` is update with instance status.
    """

    if type(sender) != type(SolutionBooking):
        return

    try:
        # Update operation (an existing review is being updated case)
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance:
            if instance.status == sender.Status.COMPLETED:
                Solution.objects.filter(id=instance.solution.id).update(
                    bookings_pending_fulfillment_count=F(
                        'bookings_pending_fulfillment_count'
                    )
                    - 1,
                )
    except sender.DoesNotExist:
        # New solution booking is being added
        Solution.objects.filter(id=instance.solution.id).update(
            bookings_pending_fulfillment_count=F('bookings_pending_fulfillment_count')
            + 1,
        )


@receiver(pre_save, sender=SolutionBooking)
def set_created_at_field_when_solution_status_from_pending_to_others(
    sender, instance=None, **kwargs
):
    """
    When solution bookings status is changed from pending to others, `started_at` field is updated to now date.
    """

    if type(sender) != type(SolutionBooking):
        return

    contract_instance = instance
    try:
        old_contract_instance = sender.objects.get(pk=contract_instance.pk)
        if old_contract_instance.status == sender.Status.PENDING:
            if instance.status != sender.Status.PENDING:
                instance.started_at = get_now_converted_google_date()
    except sender.DoesNotExist:
        if instance.status != sender.Status.PENDING:
            instance.started_at = datetime.datetime.now().date()


@receiver(post_delete, sender=SolutionBooking)
def decrease_bookings_pending_fulfillment_count_field_of_solution(
    sender, instance=None, **kwargs
):
    contract_instance = instance
    if contract_instance.status != sender.Status.COMPLETED:
        Solution.objects.filter(id=contract_instance.solution.id).update(
            bookings_pending_fulfillment_count=F('bookings_pending_fulfillment_count')
            - 1,
        )


def decrease_status_count_of_solution(solution_booking):
    """
    Decreasing solution's status count of solution booking instance
    """
    solution_id = solution_booking.solution_id
    if solution_booking.rating == -1:
        Solution.objects.filter(id=solution_id).update(sad_count=F('sad_count') - 1)
    elif solution_booking.rating == 0:
        Solution.objects.filter(id=solution_id).update(
            neutral_count=F('neutral_count') - 1
        )
    elif solution_booking.rating == 1:
        Solution.objects.filter(id=solution_id).update(happy_count=F('happy_count') - 1)


def increase_status_count_of_solution(solution_booking):
    """
    Increasing solution's status count of solution booking instance
    """
    solution_id = solution_booking.solution_id
    if solution_booking.rating == -1:
        Solution.objects.filter(id=solution_id).update(sad_count=F('sad_count') + 1)
    elif solution_booking.rating == 0:
        Solution.objects.filter(id=solution_id).update(
            neutral_count=F('neutral_count') + 1
        )
    elif solution_booking.rating == 1:
        Solution.objects.filter(id=solution_id).update(happy_count=F('happy_count') + 1)


@receiver(pre_save, sender=SolutionBooking)
def status_count_update_for_solution_booking(sender, instance=None, **kwargs):
    """
    When a new solution booking is added, the status count of solution is recalculated and updated.
    """
    if type(sender) != type(SolutionBooking):
        return
    solution_booking_instance = instance
    try:
        old_solution_booking_instance = sender.objects.get(
            id=solution_booking_instance.id
        )
        if old_solution_booking_instance:
            # When a old solution booking is being updated.
            if solution_booking_instance.rating != old_solution_booking_instance.rating:
                """
                If new solution booking rating is different from old one,
                then old status type count should be decreased
                and new status type count should be increased in solution.
                """
                decrease_status_count_of_solution(old_solution_booking_instance)
                increase_status_count_of_solution(solution_booking_instance)

    except sender.DoesNotExist:
        # New solution booking is being added
        increase_status_count_of_solution(solution_booking_instance)


@receiver(post_delete, sender=SolutionBooking)
def decrease_status_type_count_of_solution(sender, instance=None, **kwargs):
    if type(sender) != type(SolutionBooking):
        return
    solution_booking_instance = instance
    decrease_status_count_of_solution(solution_booking_instance)


# https://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave
request_finished.connect(
    status_count_update_for_solution_booking,
    dispatch_uid="status_count_update_for_solution_booking",
)

# https://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave
request_finished.connect(
    count_update_for_new_or_complete_booking,
    dispatch_uid="count_update_for_new_or_complete_booking",
)
