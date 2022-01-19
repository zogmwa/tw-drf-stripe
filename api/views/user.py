import stripe
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from djstripe.models import Customer as StripeCustomer
from djstripe.models import Subscription as StripeSubscription
from api.utils.models import get_or_none
from rest_framework.response import Response
from api.models import User
from api.models.solution import Solution
from api.models.solution_booking import SolutionBooking
from api.serializers.user import UserSerializer
from api.serializers.solution_booking import AuthenticatedSolutionBookingSerializer
from api.permissions.user_permissions import AllowOwnerOrAdminOrStaff


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    permission_classes = [AllowOwnerOrAdminOrStaff]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    @action(detail=True, permission_classes=[IsAuthenticated], methods=['get'])
    def bookings(self, request, *args, **kwargs):
        """
        If the user wants to get solution bookings list:
        http://127.0.0.1:8000/users/<username>/bookings/
        http://127.0.0.1:8000/users/<username>/bookings/?id=<solution_booking_id>
        """
        contract_id = request.GET.get('id', '')
        context_serializer = {'request': request}
        if contract_id:
            solution_booking_queryset = SolutionBooking.objects.filter(
                booked_by__username=kwargs['username'], id=contract_id
            )
        else:
            solution_booking_queryset = SolutionBooking.objects.filter(
                booked_by__username=kwargs['username']
            )

        solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
            solution_booking_queryset, context=context_serializer, many=True
        )

        return Response(solution_booking_serializer.data)

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def attach_card(self, request, *args, **kwargs):
        if request.data.get('payment_method'):
            user = self.request.user
            if user.stripe_customer is None:
                if user.first_name is None and user.last_name is None:
                    username = user.username
                else:
                    username = '{} {}'.format(user.first_name, user.last_name)
                # Create user's customer
                stripe_customer = stripe.Customer.create(
                    email=user.email, name=username
                )
                djstripe_customer = StripeCustomer.sync_from_stripe_data(
                    stripe_customer
                )
                user.stripe_customer = djstripe_customer
                user.save()
            else:
                stripe_customer = user.stripe_customer

            # Attact payment method to customer
            stripe_payment_method = stripe.PaymentMethod.attach(
                request.data.get('payment_method'), customer=stripe_customer.id
            )

            if stripe_customer.default_payment_method is None:
                stripe_customer_with_payment_method = stripe.Customer.modify(
                    stripe_customer.id,
                    invoice_settings={
                        'default_payment_method': stripe_payment_method.id,
                    },
                )
                StripeCustomer.sync_from_stripe_data(
                    stripe_customer_with_payment_method
                )
                return Response({'status': 'payment method attached successfully'})
            else:
                return Response({'status': 'payment method attached successfully'})
        else:
            return Response(
                data={"detail": "incorrect payment method"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['get'])
    def payment_methods(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            return Response({'has_payment_method': None})
        else:
            if user.stripe_customer:
                customer_payment_methods = stripe.PaymentMethod.list(
                    customer=user.stripe_customer.id,
                    type="card",
                )
                payment_methods = customer_payment_methods.get('data')
                return_payment_methods = []
                for payment_method in payment_methods:
                    return_payment_methods.append(
                        {
                            "id": payment_method.id,
                            "brand": payment_method.card.brand,
                            "last4": payment_method.card.last4,
                            "exp_month": payment_method.card.exp_month,
                            "exp_year": payment_method.card.exp_year,
                            "default_payment_method": user.stripe_customer.default_payment_method.id
                            == payment_method.id,
                        }
                    )
                return Response(
                    {
                        'has_payment_method': user.stripe_customer.default_payment_method
                        is not None,
                        'payment_methods': return_payment_methods,
                    }
                )
            else:
                return Response({'has_payment_method': None})

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def subscribe_payment(self, request, *args, **kwargs):
        user = request.user
        if user.stripe_customer:
            if request.data.get('payment_method'):
                referring_user_id = request.data.get('referring_user')
                solution_slug = request.data.get('slug')
                solution = get_or_none(Solution, slug=solution_slug)
                if solution is None:
                    return Response(
                        data={"detail": "incorrect solution"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    stripe_subscription = stripe.Subscription.create(
                        customer=user.stripe_customer.id,
                        items=[{'price': solution.primary_stripe_price.id}],
                        expand=['latest_invoice.payment_intent'],
                    )
                    djstripe_subscription = StripeSubscription.sync_from_stripe_data(
                        stripe_subscription
                    )
                    solution_booking = SolutionBooking.objects.create(
                        booked_by=request.user,
                        solution=solution,
                        stripe_subscription=djstripe_subscription,
                        referring_user=get_or_none(User, id=referring_user_id),
                    )
                    return Response({'solution_booking_id': solution_booking.id})
            else:
                return Response(
                    data={"detail": "missing payment method"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                data={
                    "detail": "The user {} is missing an associated stripe_customer".format(
                        user.username
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
