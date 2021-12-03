from api.models.solution_booking import SolutionBooking
from payments import models
from django.core import mail


class TestCheckoutSessionWebhook:
    def check_mail_content(self, subject, body, to):
        email = mail.outbox[0]
        assert email.to == to
        assert email.body == body
        assert email.subject == subject

    def test_checkout_session_completed(
        self, example_solution_booking, example_event, admin_user
    ):
        example_solution_booking.stripe_session_id = example_event['data']['object'][
            'id'
        ]
        example_solution_booking.save()
        models.checkout_session_completed_handler(example_event)
        solution_booking = SolutionBooking.objects.get(
            stripe_session_id=example_event['data']['object']['id'],
        )
        assert solution_booking.is_payment_completed is True
        self.check_mail_content(
            'Solution Booked',
            'Solution Booking ID: {}'.format(example_solution_booking.id),
            [admin_user.email],
        )

    def test_checkout_session_async_payment_succeed(
        self, example_solution_booking, example_event, admin_user
    ):
        example_solution_booking.stripe_session_id = example_event['data']['object'][
            'id'
        ]
        example_solution_booking.save()
        models.checkout_session_async_payment_succeeded(example_event)
        solution_booking = SolutionBooking.objects.get(
            stripe_session_id=example_event['data']['object']['id'],
        )
        assert solution_booking.is_payment_completed is True
        self.check_mail_content(
            'Solution Booked',
            'Solution Booking ID: {}'.format(example_solution_booking.id),
            [admin_user.email],
        )

    def test_checkout_session_async_payment_failed(
        self, example_solution_booking, example_event, admin_user
    ):
        example_event['data']['object']['payment_status'] = 'failed'
        example_solution_booking.stripe_session_id = example_event['data']['object'][
            'id'
        ]
        example_solution_booking.save()
        models.checkout_session_async_payment_failed(example_event)
        self.check_mail_content(
            'There was a problem with your order',
            'Kindly retry order or reach out to contact@taggedweb.com Booking Reference: {}'.format(
                example_solution_booking.id
            ),
            [example_solution_booking.booked_by.email],
        )
