from django.db import models

# Create your models here.
from djstripe import webhooks


@webhooks.handler("checkout.session.completed")
def checkout_session_completed_handler(event, **kwargs):
    # TODO: Create a SolutionBooking object with payment pending
    print("We should probably notify the user at this point by redirecting to frontend")
