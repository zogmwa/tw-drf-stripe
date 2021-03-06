import stripe
from django.contrib.sites.models import Site
from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.conf import settings
from furl import furl

from api.utils.models import get_or_none
from api.models.solution_booking import SolutionBooking
from api.models.solution import Solution
from api.models.user import User


if settings.STRIPE_LIVE_MODE:
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
else:
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class CreateStripeCheckoutSession(APIView):
    """
    Will take a solution_price_id and return a corresponding Checkout page from that.
    The frontend can redirect the user to that checkout page once this id is obtained.

    Example:

        curl -H "Authorization: <Token/Bearer> <replace_with_token>" -H 'Content-Type: application/json' -X POST \
         http://localhost:8000/solution-price-checkout/<pay_now_stripe_price_id>

    Later on we may want to move this under solution_prices API endpoint (if we want to add that). As of date of
    this comment I don't expect too many prices for a given solution.
    """

    # TODO: Later we may want to change this to allow authenticated requests only otherwise how will we know which
    # user started a payment flow.
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        In an alternate reality we could read the solution.id via the POST params but for some reason it was easier for
        the frontend to pass the stripe_price_id instead.
        """
        stripe_price_id = kwargs['pay_now_stripe_price_id']
        referring_user_id = self.request.query_params.get('r')
        solution = Solution.objects.select_related('stripe_primary_price').get(
            stripe_primary_price__id=stripe_price_id
        )
        prepaid_solution_price = solution.stripe_primary_price
        active_site_obj = Site.objects.get(id=settings.SITE_ID)
        active_site = furl('https://{}'.format(active_site_obj.domain))

        # Convert cents to dollars
        # TODO: This may need a change when we move to non USD payments
        prepaid_solution_price_dollars = prepaid_solution_price.unit_amount / 100
        payment_cancel_url = active_site / 'payment-cancel'
        payment_cancel_url.args['solution'] = solution.slug
        payment_cancel_url.args['r'] = referring_user_id

        referring_user = get_or_none(User, id=referring_user_id)
        solution_booking = SolutionBooking.objects.create(
            booked_by=request.user,
            solution=solution,
            status=SolutionBooking.Status.PENDING,
            is_payment_completed=False,
            price_at_booking=prepaid_solution_price_dollars,
            referring_user=referring_user,
        )

        payment_success_url = active_site
        payment_success_url.path.segments = [
            'profile',
            'contracts',
            solution_booking.id,
        ]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': prepaid_solution_price.id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=payment_success_url.url,
            cancel_url=payment_cancel_url.url,
            customer_email=request.user.email,
        )

        # This endpoint just returns the checkout url, the frontend should do the redirect
        response_data = {'checkout_page_url': checkout_session.url}

        solution_booking.stripe_session_id = checkout_session.id
        solution_booking.save()

        return JsonResponse(response_data)


# TODO: Add a backend API endpoint to allow the frontend to exchange a checkout_session_id for a user email
