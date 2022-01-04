from django.core.mail import send_mail
from django.conf import settings

from api.models.solution_booking import SolutionBooking


def fulfill_order(stripe_session_id: str) -> None:
    solution_booking = SolutionBooking.objects.get(
        stripe_session_id=stripe_session_id,
    )
    solution_booking.is_payment_completed = True
    solution_booking.save()

    solution_poc_email = (
        solution_booking.solution.point_of_contact.email or 'pranjal@taggedweb.com'
    )

    send_mail(
        subject='Solution Booked',
        message='Solution Booking ID: {}. Here is the link to the solution that you booked: {}'.format(
            solution_booking.id,
            _get_solution_url_from_slug(solution_booking.solution.slug),
        ),
        from_email='noreply@taggedweb.com',
        recipient_list=[solution_poc_email],
    )


def email_customer_about_failed_payment(stripe_session_id):
    solution_booking = SolutionBooking.objects.get(
        stripe_session_id=stripe_session_id,
    )

    send_mail(
        subject='There was a problem with your order',
        message='Kindly retry order or reach out to contact@taggedweb.com Booking Reference: {}. Here is the link to the solution that you attempted booking: {}'.format(
            solution_booking.id,
            _get_solution_url_from_slug(solution_booking.solution.slug),
        ),
        from_email='noreply@taggedweb.com',
        recipient_list=[solution_booking.booked_by.email],
    )


def _get_solution_url_from_slug(solution_slug: str) -> str:
    return 'https://{}/solutions/{}'.format(
        settings.BASE_FRONTEND_URL,
        solution_slug,
    )
