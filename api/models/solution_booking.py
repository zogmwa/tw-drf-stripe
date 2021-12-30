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
        CANCELLED = 'Cancelled'
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
        default=Status.CANCELLED,
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
            if (old_instance.status != sender.Status.CANCELLED) and (
                instance.status == sender.Status.COMPLETED
            ):
                Solution.objects.filter(id=instance.solution.id).update(
                    bookings_pending_fulfillment_count=F(
                        'bookings_pending_fulfillment_count'
                    )
                    - 1,
                )
            elif (
                (old_instance.status == sender.Status.CANCELLED)
                and (instance.status != sender.Status.CANCELLED)
                and (instance.status != sender.Status.COMPLETED)
            ):
                Solution.objects.filter(id=instance.solution.id).update(
                    bookings_pending_fulfillment_count=F(
                        'bookings_pending_fulfillment_count'
                    )
                    + 1,
                )
            elif (old_instance.status != sender.Status.CANCELLED) and (
                instance.status == sender.Status.CANCELLED
            ):
                Solution.objects.filter(id=instance.solution.id).update(
                    bookings_pending_fulfillment_count=F(
                        'bookings_pending_fulfillment_count'
                    )
                    - 1,
                )
            elif (old_instance.status == sender.Status.COMPLETED) and (
                instance.status != sender.Status.COMPLETED
            ):
                Solution.objects.filter(id=instance.solution.id).update(
                    bookings_pending_fulfillment_count=F(
                        'bookings_pending_fulfillment_count'
                    )
                    + 1,
                )
    except sender.DoesNotExist:
        # New solution booking is being added
        if instance.status != SolutionBooking.Status.CANCELLED:
            Solution.objects.filter(id=instance.solution.id).update(
                bookings_pending_fulfillment_count=F(
                    'bookings_pending_fulfillment_count'
                )
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
            if (instance.status != sender.Status.PENDING) and (
                instance.status != sender.Status.CANCELLED
            ):
                instance.started_at = get_now_converted_google_date()

    except sender.DoesNotExist:
        if (instance.status != sender.Status.PENDING) and (
            instance.status != sender.Status.CANCELLED
        ):
            instance.started_at = datetime.datetime.now().date()


@receiver(post_save, sender=SolutionBooking)
def send_email_to_user_and_provider_when_solution_type_is_consultation(
    sender, instance=None, created=False, **kwargs
):

    if created:
        solution = instance.solution
        if solution.type == Solution.Type.CONSULTATION:
            if solution.point_of_contact.email is None:
                send_mail(
                    subject='{} needs consultation'.format(solution.title),
                    message='{} {} user needs consultation about {}'.format(
                        instance.booked_by.first_name,
                        instance.booked_by.last_name,
                        solution.title,
                    ),
                    from_email='noreply@taggedweb.com',
                    recipient_list=['contact@taggedweb.com'],
                )
            else:
                send_mail(
                    subject='{} needs consultation'.format(solution.title),
                    message='{} {} user needs consultation about {}'.format(
                        instance.booked_by.first_name,
                        instance.booked_by.last_name,
                        solution.title,
                    ),
                    from_email='noreply@taggedweb.com',
                    recipient_list=[solution.point_of_contact.email],
                )

            send_mail(
                subject='Your consultation has received',
                message='Your consultation about {} has received. We will reply in shortly'.format(
                    solution.title,
                ),
                from_email='noreply@taggedweb.com',
                recipient_list=[instance.booked_by.email],
            )


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


# https://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave
request_finished.connect(
    count_update_for_new_or_complete_booking,
    dispatch_uid="count_update_for_new_or_complete_booking",
)

request_finished.connect(
    send_email_to_user_and_provider_when_solution_type_is_consultation,
    dispatch_uid="send_email_to_user_and_provider_when_solution_type_is_consultation",
)
