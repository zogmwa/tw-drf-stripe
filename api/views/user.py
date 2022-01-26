import stripe
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from djstripe.models import Customer as StripeCustomer
from djstripe.models import Subscription as StripeSubscription
from djstripe.models import SubscriptionItem as StripeSubscriptionItem
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
                    customer_name = user.username
                else:
                    customer_name = '{} {}'.format(user.first_name, user.last_name)

                stripe_customer = stripe.Customer.create(
                    email=user.email, name=customer_name
                )
                djstripe_customer = StripeCustomer.sync_from_stripe_data(
                    stripe_customer
                )
                user.stripe_customer = djstripe_customer
                user.save()
            else:
                stripe_customer = user.stripe_customer

            # Check customer already has this payment method.
            attaching_stripe_payment_method = stripe.PaymentMethod.retrieve(
                request.data.get('payment_method')
            )
            customer_payment_methods = stripe.PaymentMethod.list(
                customer=user.stripe_customer.id,
                type="card",
            )
            payment_methods = customer_payment_methods.get('data')
            for payment_method in payment_methods:
                if (
                    payment_method.card.fingerprint
                    == attaching_stripe_payment_method.card.fingerprint
                ):
                    return Response(
                        {'status': 'You have already attached this payment.'}
                    )

            # Attach payment method to customer.
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
                return Response({'status': 'payment method associated successfully'})
            else:
                return Response({'status': 'payment method associated successfully'})
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
                        items=[{'price': solution.stripe_primary_price.id}],
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

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def detach_payment_method(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            return Response({'has_payment_method': None})
        else:
            if user.stripe_customer:
                # Detach payment method to customer.
                stripe.PaymentMethod.detach(request.data.get('payment_method'))
                customer_payment_methods = stripe.PaymentMethod.list(
                    customer=user.stripe_customer.id,
                    type="card",
                )
                payment_methods = customer_payment_methods.get('data')
                if len(payment_methods) == 0:
                    stripe_customer_with_payment_method = stripe.Customer.modify(
                        user.stripe_customer.id,
                        invoice_settings={},
                    )
                    StripeCustomer.sync_from_stripe_data(
                        stripe_customer_with_payment_method
                    )
                    user.stripe_customer.default_payment_method = None
                    user.stripe_customer.save()
                    return Response({'data': [], 'has_payment_method': True})
                else:
                    if (
                        user.stripe_customer.default_payment_method.id
                        == request.data.get('payment_method')
                    ):
                        stripe_customer_with_payment_method = stripe.Customer.modify(
                            user.stripe_customer.id,
                            invoice_settings={
                                'default_payment_method': payment_methods[0].id,
                            },
                        )
                        StripeCustomer.sync_from_stripe_data(
                            stripe_customer_with_payment_method
                        )
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
                            'data': return_payment_methods,
                            'has_payment_method': True,
                        }
                    )
            else:
                return Response({'has_payment_method': None})

    @action(detail=True, permission_classes=[IsAuthenticated], methods=['get'])
    def provider_bookings(self, request, *args, **kwargs):
        """
        If the user wants to get solution bookings list:
        http://127.0.0.1:8000/users/<username>/provider_bookings/
        http://127.0.0.1:8000/users/<username>/provider_bookings/?id=<solution_booking_id>
        """
        contract_id = request.GET.get('id', '')
        context_serializer = {'request': request}
        if contract_id:
            solution_booking = SolutionBooking.objects.get(id=contract_id)
            stripe_subscription = solution_booking.stripe_subscription

            stripe_subscription_item = StripeSubscriptionItem.objects.filter(
                subscription__id=stripe_subscription.id
            )[0]
            subscription_usage = stripe.SubscriptionItem.list_usage_record_summaries(
                stripe_subscription_item.id,
            )

            tracking_times = subscription_usage.get('data')
            return_tracking_times = []
            for tracking_time in tracking_times:
                if tracking_time.period.start:
                    return_tracking_times.append(
                        {
                            'start': tracking_time.period.start,
                            'end': tracking_time.period.end,
                            'total_usage': tracking_time.total_usage,
                        }
                    )

            solution_booking_queryset = SolutionBooking.objects.get(
                solution__point_of_contact__username=kwargs['username'],
                id=contract_id,
            )

            solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
                solution_booking_queryset, context=context_serializer
            )
            return Response(
                {
                    'current_period_start': stripe_subscription.current_period_start,
                    'current_period_end': stripe_subscription.current_period_end,
                    'tracking_times': return_tracking_times,
                    'booking_data': solution_booking_serializer.data,
                }
            )
        else:
            solution_booking_queryset = SolutionBooking.objects.filter(
                solution__point_of_contact__username=kwargs['username']
            )

        solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
            solution_booking_queryset, context=context_serializer, many=True
        )

        return Response(solution_booking_serializer.data)
