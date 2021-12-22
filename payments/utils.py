from django.core.mail import send_mail

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
    SOLUTION_URL = 'https://taggedweb.com/solutions/{}'.format(
        solution_booking.solution.slug
    )
    send_mail(
        subject='Solution Booked',
        message='Solution Booking ID: {}. Here is the link to the solution that you attempted booking: {}'.format(
            solution_booking.id,
            SOLUTION_URL,
        ),
        from_email='noreply@taggedweb.com',
        recipient_list=[solution_poc_email],
    )


def email_customer_about_failed_payment(stripe_session_id):
    solution_booking = SolutionBooking.objects.get(
        stripe_session_id=stripe_session_id,
    )
    SOLUTION_URL = 'https://taggedweb.com/solutions/{}'.format(
        solution_booking.solution.slug
    )

    send_mail(
        subject='There was a problem with your order',
        message='Kindly retry order or reach out to contact@taggedweb.com Booking Reference: {}. Here is the link to the solution that you attempted booking: {}'.format(
            solution_booking.id, SOLUTION_URL
        ),
        from_email='noreply@taggedweb.com',
        recipient_list=[solution_booking.booked_by.email],
    )
