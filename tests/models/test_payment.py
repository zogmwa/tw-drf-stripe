from api.models.solution_booking import SolutionBooking
from payments import models
from django.core import mail

from payments.utils import _get_solution_url_from_slug


class TestCheckoutSessionWebhook:
    def check_mail_content(self, subject, to, body):
        email = mail.outbox[0]
        assert email.to == to
        assert email.subject == subject
        assert email.body == body

    def test_checkout_session_completed(
        self, example_solution_booking, example_event, admin_user
    ):
        example_solution_booking.stripe_session_id = example_event.data['object']['id']
        example_solution_booking.save()
        models.checkout_session_completed_handler(example_event)
        solution_booking = SolutionBooking.objects.get(
            stripe_session_id=example_event.data['object']['id'],
        )
        assert solution_booking.is_payment_completed is True

        self.check_mail_content(
            'Solution Booked',
            [admin_user.email],
            'Solution Booking ID: {}. Here is the link to the solution that you booked: {}'.format(
                solution_booking.id,
                _get_solution_url_from_slug(example_solution_booking.solution.slug),
            ),
        )

    def test_checkout_session_async_payment_succeed(
        self, example_solution_booking, example_event, admin_user
    ):
        example_solution_booking.stripe_session_id = example_event.data['object']['id']
        example_solution_booking.save()
        models.checkout_session_async_payment_succeeded(example_event)
        solution_booking = SolutionBooking.objects.get(
            stripe_session_id=example_event.data['object']['id'],
        )
        assert solution_booking.is_payment_completed is True

        self.check_mail_content(
            'Solution Booked',
            [admin_user.email],
            'Solution Booking ID: {}. Here is the link to the solution that you booked: {}'.format(
                solution_booking.id,
                _get_solution_url_from_slug(example_solution_booking.solution.slug),
            ),
        )

    def test_checkout_session_async_payment_failed(
        self, example_solution_booking, example_event, admin_user
    ):
        example_event.data['object']['payment_status'] = 'failed'
        example_solution_booking.stripe_session_id = example_event.data['object']['id']
        example_solution_booking.save()
        models.checkout_session_async_payment_failed(example_event)

        self.check_mail_content(
            'There was a problem with your order',
            [example_solution_booking.booked_by.email],
            'Kindly retry order or reach out to contact@taggedweb.com Booking Reference: {}. Here is the link to the solution that you attempted booking: {}'.format(
                example_solution_booking.id,
                _get_solution_url_from_slug(example_solution_booking.solution.slug),
            ),
        )
