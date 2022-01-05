from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from api.models.solution_booking import SolutionBooking


def fulfill_order(stripe_session_id: str) -> None:
    solution_booking = SolutionBooking.objects.get(
        stripe_session_id=stripe_session_id,
    )
    solution_booking.is_payment_completed = True
    solution_booking.save()
    solution = solution_booking.solution

    point_of_contact = solution.point_of_contact
    customer = solution_booking.booked_by

    email_params = {
        'customer': customer,
        'point_of_contact': point_of_contact,
        'solution': solution,
        'solution_booking': solution_booking,
        'solution_url': _get_solution_url_from_slug(solution_booking.solution.slug),
    }
    customer_email_msg_plain = render_to_string(
        'emails/booking_confirmation_customer.txt',
        email_params,
    )
    customer_email_msg_html = render_to_string(
        'emails/booking_confirmation_customer.html',
        email_params,
    )

    # Send a confirmation email to the customer who booked the Solution
    send_mail(
        subject='TaggedWeb.com Booking Confirmation. Booking ID: {}',
        html_message=customer_email_msg_html,
        message=customer_email_msg_plain,
        from_email='noreply@taggedweb.com',
        recipient_list=[customer.email],
    )

    # Send email to Point of Contact on the solution to let them know this solution has been booked
    send_mail(
        subject='Solution booked on TaggedWeb. Booking ID: {}'.format(
            solution_booking.id
        ),
        message='Booking ID: {} \n Solution URL: {} \n Customer Email: {}. \n Kindly follow up with the customer to fullfill the service'.format(
            solution_booking.id,
            _get_solution_url_from_slug(solution_booking.solution.slug),
            customer.email,
        ),
        from_email='contact@taggedweb.com',
        recipient_list=[point_of_contact.email],
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
    return 'https://{}/solution/{}'.format(
        settings.BASE_FRONTEND_URL,
        solution_slug,
    )
