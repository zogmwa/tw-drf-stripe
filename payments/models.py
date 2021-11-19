from django.db import models

# Create your models here.
from djstripe import webhooks

from payments.utils import fulfill_order


@webhooks.handler("checkout.session")
def checkout_session_completed_handler(event, **kwargs):
    # TODO: Create a SolutionBooking object with payment pending

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        fulfill_order(session)

    print("We should probably notify the user at this point by redirecting to frontend")
