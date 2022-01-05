from typing import List

from api.models.solution_booking import SolutionBooking
from payments import models
from django.core import mail


class TestCheckoutSessionWebhook:
    def _verify_outbox(self, to_sequence: List[List[str]]):
        # Verify that the email has been sent to the intended recipients in the right sequence
        assert [message.to for message in mail.outbox] == to_sequence

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

    def test_checkout_session_async_payment_succeed(
        self,
        example_solution_booking,
        example_event,
        admin_user,
        user_and_password_with_first_last_name,
    ):
        customer = user_and_password_with_first_last_name[0]
        example_solution_booking.stripe_session_id = example_event.data['object']['id']
        example_solution_booking.booked_by = customer
        example_solution_booking.save()

        models.checkout_session_async_payment_succeeded(example_event)

        solution_booking = SolutionBooking.objects.get(
            stripe_session_id=example_event.data['object']['id'],
        )
        assert solution_booking.is_payment_completed is True

        self._verify_outbox([[customer.email], [admin_user.email]])

    def test_checkout_session_async_payment_failed(
        self, example_solution_booking, example_event, admin_user
    ):
        example_event.data['object']['payment_status'] = 'failed'
        example_solution_booking.stripe_session_id = example_event.data['object']['id']
        example_solution_booking.save()

        models.checkout_session_async_payment_failed(example_event)

        expected_to = [example_solution_booking.booked_by.email]
        self._verify_outbox([expected_to])
