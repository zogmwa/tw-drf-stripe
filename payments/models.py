from djstripe import webhooks

from api.models.solution_booking import SolutionBooking
from payments.utils import fulfill_order, email_customer_about_failed_payment


@webhooks.handler('checkout.session.completed')
def checkout_session_completed_handler(event, **kwargs):
    """
    This is triggered when the user completes the Stripe checkout flow and is shown the success page.
    This doesn't necessarily meant that the payment is completed.
    """
    session = event['data']['object']
    stripe_session_id = session['id']

    # Check if the order is already paid (e.g., from a card payment)
    #
    # A delayed notification payment will have an `unpaid` status, as
    # you're still waiting for funds to be transferred from the customer's
    # account.
    if session.payment_status == "paid":
        fulfill_order(stripe_session_id)


@webhooks.handler('checkout.session.async_payment_succeeded')
def checkout_session_async_payment_succeeded(event, **kwargs):
    session = event['data']['object']
    stripe_session_id = session['id']
    fulfill_order(stripe_session_id)


@webhooks.handler('checkout.session.async_payment_failed')
def checkout_session_async_payment_failed(event, **kwargs):
    session = event['data']['object']
    stripe_session_id = session['id']
    # Send an email to the customer asking them to retry their order
    email_customer_about_failed_payment(stripe_session_id)
