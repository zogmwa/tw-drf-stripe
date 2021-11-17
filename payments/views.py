import stripe
from django.contrib.sites.models import Site
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.conf import settings
from djstripe import webhooks

from api.models.solution_price import SolutionPrice

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class CreateStripeCheckoutSession(APIView):
    """
    Will take a solution_price_id and return a corresponding Checkout page from that.
    The frontend can redirect the user to that checktout page once this id is obtained.

    Later on we may want to move this under solution_prices API endpoint (if we want to add that). As of date of
    this comment I don't expect too many prices for a given solution.
    """

    # TODO: Later we may want to change this to allow authenticated requests only otherwise how will we know which
    # user started a payment flow.
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        tweb_solution_price_id = kwargs['solution_price_id']
        solution_price = SolutionPrice.objects.get(id=tweb_solution_price_id)
        active_site = Site.objects.get(id=settings.SITE_ID)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': solution_price.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='https://{}/payment-success/'.format(active_site.domain),
            cancel_url='https://{}/payment-cancel/'.format(active_site.domain),
        )

        response_data = {'checkout_page_url': checkout_session.url}
        return JsonResponse(response_data)


@webhooks.handler("checkout.session.completed")
def my_handler(event, **kwargs):
    # TODO: Create a SolutionBooking object with payment pending
    print("We should probably notify the user at this point by redirecting to frontend")
