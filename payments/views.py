import stripe
from django.contrib.sites.models import Site
from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.conf import settings

from api.models.solution_booking import SolutionBooking
from api.models.solution import Solution
from djstripe.models import Price as StripePrice
from .models import checkout_session_completed_handler


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class CreateStripeCheckoutSession(APIView):
    """
    Will take a solution_price_id and return a corresponding Checkout page from that.
    The frontend can redirect the user to that checkout page once this id is obtained.

    Example:

        curl -H "Authorization: <Token/Bearer> <replace_with_token>" -H 'Content-Type: application/json' -X POST \
         http://localhost:8000/solution-price-checkout/<solution_price_id>

    Later on we may want to move this under solution_prices API endpoint (if we want to add that). As of date of
    this comment I don't expect too many prices for a given solution.
    """

    # TODO: Later we may want to change this to allow authenticated requests only otherwise how will we know which
    # user started a payment flow.
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        tweb_solution_price_id = kwargs['solution_price_id']
        pay_now_price = StripePrice(id=tweb_solution_price_id)
        solution = Solution.objects.get(pay_now_price__id=tweb_solution_price_id)
        active_site_obj = Site.objects.get(id=settings.SITE_ID)
        active_site = 'https://{}'.format(active_site_obj.domain)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': pay_now_price.id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=active_site
            + '/payment-success/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=active_site
            + '/payment-cancel/?session_id={CHECKOUT_SESSION_ID}&solution='
            + solution.slug,
            customer_email=request.user.email,
        )

        # This endpoint just returns the checkout url, the frontend should do the redirect
        response_data = {'checkout_page_url': checkout_session.url}

        SolutionBooking.objects.create(
            booked_by=request.user,
            solution=solution,
            status=SolutionBooking.Status.PENDING,
            is_payment_completed=False,
            price_at_booking=pay_now_price.unit_amount,
            stripe_session_id=checkout_session.id,
        )

        return JsonResponse(response_data)


# TODO: Add a backend API endpoint to allow the frontend to exchange a checkout_session_id for a user email