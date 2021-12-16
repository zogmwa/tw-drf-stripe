from django.core.mail import send_mail

from api.models.solution_booking import SolutionBooking

SOLUTION_BASE_ENDPOINT = 'https://taggedweb.com/solutions/'
SOLUTION_DETAIL_MSG = ', to view the solution for which booking was done please click on this link:{}'.format(
    SOLUTION_BASE_ENDPOINT
)


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
        message='Solution Booking ID: {}{}{}'.format(
            solution_booking.id, SOLUTION_DETAIL_MSG, solution_booking.solution.slug
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
        message='Kindly retry order or reach out to contact@taggedweb.com Booking Reference: {}{}{}'.format(
            solution_booking.id, SOLUTION_DETAIL_MSG, solution_booking.solution.slug
        ),
        from_email='noreply@taggedweb.com',
        recipient_list=[solution_booking.booked_by.email],
    )
