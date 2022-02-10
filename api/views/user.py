import math
import pytz
import uuid
import stripe
import datetime
import pandas as pd
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.utils.models import get_or_none
from api.utils.convert_str_to_date import (
    convert_string_to_datetime,
)
from api.models import User
from api.models.solution import Solution
from api.models.time_tracked_day import TimeTrackedDay
from api.models.solution_booking import SolutionBooking
from api.models.partner_customer import PartnerCustomer
from djstripe.models import Customer as StripeCustomer
from djstripe.models import Subscription as StripeSubscription
from djstripe.models import SubscriptionItem as StripeSubscriptionItem
from api.serializers.user import UserSerializer
from api.serializers.time_tracked_day import TimeTrackedDaySerializer
from api.serializers.solution_booking import AuthenticatedSolutionBookingSerializer
from api.permissions.user_permissions import AllowOwnerOrAdminOrStaff


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    @staticmethod
    def _attach_payment_method_to_stripe_customer(payment_method, stripe_customer):
        # Check customer already has this payment method.
        attaching_stripe_payment_method = stripe.PaymentMethod.retrieve(payment_method)
        customer_payment_methods = stripe.PaymentMethod.list(
            customer=stripe_customer.id,
            type="card",
        )
        stripe_payment_methods = customer_payment_methods.get('data')
        for stripe_payment_method in stripe_payment_methods:
            if (
                stripe_payment_method.card.fingerprint
                == attaching_stripe_payment_method.card.fingerprint
            ):
                return {'status': 'You have already attached this payment.'}

        # Attach payment method to customer.
        stripe_payment_method = stripe.PaymentMethod.attach(
            payment_method, customer=stripe_customer.id
        )

        if stripe_customer.default_payment_method is None:
            stripe_customer_with_payment_method = stripe.Customer.modify(
                stripe_customer.id,
                invoice_settings={
                    'default_payment_method': stripe_payment_method.id,
                },
            )
            StripeCustomer.sync_from_stripe_data(stripe_customer_with_payment_method)
            return {'status': 'payment method associated successfully'}
        else:
            return {'status': 'payment method associated successfully'}

    @staticmethod
    def _attach_payment_method_to_loggin_user(user, payment_method):
        if user.stripe_customer is None:
            if user.first_name is None and user.last_name is None:
                customer_name = user.username
            else:
                customer_name = '{} {}'.format(user.first_name, user.last_name)

            stripe_customer = stripe.Customer.create(
                email=user.email, name=customer_name
            )
            djstripe_customer = StripeCustomer.sync_from_stripe_data(stripe_customer)
            user.stripe_customer = djstripe_customer
            user.save()
        else:
            stripe_customer = user.stripe_customer

        return_data = UserViewSet._attach_payment_method_to_stripe_customer(
            payment_method, stripe_customer
        )

        return return_data

    @staticmethod
    def _get_provider_booking_detail_data(contract_id, username, context_serializer):
        try:
            solution_booking = SolutionBooking.objects.get(id=contract_id)
            booking_trackings_queryset = TimeTrackedDay.objects.filter(
                solution_booking=solution_booking
            )
            booking_trackings_serializer = TimeTrackedDaySerializer(
                booking_trackings_queryset, many=True
            )
            solution_booking_queryset = SolutionBooking.objects.get(
                solution__point_of_contact__username=username,
                id=contract_id,
            )
            solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
                solution_booking_queryset, context=context_serializer
            )
            stripe_subscription = solution_booking.stripe_subscription
            if stripe_subscription is not None:
                return {
                    'current_period_start': stripe_subscription.current_period_start,
                    'current_period_end': stripe_subscription.current_period_end,
                    'tracking_times': booking_trackings_serializer.data,
                    'booking_data': solution_booking_serializer.data,
                }
            else:
                return {'booking_data': solution_booking_serializer.data}

        except SolutionBooking.DoesNotExist:
            return {'error': 'Contract does not exist'}

    @staticmethod
    def _save_tracked_time_instance(
        tracking_time_data, stripe_subscription, solution_booking, user
    ):
        utc = pytz.UTC
        updated_count = 0
        for tracking_time in tracking_time_data:
            tracked_time = math.ceil(float(tracking_time['tracked_hours']) * 10) / 10
            date = convert_string_to_datetime(tracking_time['date'])
            if (utc.localize(date) >= stripe_subscription.current_period_start) and (
                utc.localize(date) < stripe_subscription.current_period_end
            ):
                TimeTrackedDay.objects.filter(
                    solution_booking=solution_booking,
                    date=date,
                ).delete()
                TimeTrackedDay.objects.create(
                    solution_booking=solution_booking,
                    date=date,
                    tracked_hours=tracked_time,
                    user=user,
                )
                updated_count = updated_count + 1

        return updated_count

    def _save_tracked_times(self, contract_id, tracking_time_data, user):
        if contract_id:
            try:
                solution_booking = SolutionBooking.objects.get(id=contract_id)
                stripe_product = solution_booking.solution.stripe_product
                stripe_subscription = solution_booking.stripe_subscription
                stripe_subscription_item = StripeSubscriptionItem.objects.filter(
                    subscription__id=stripe_subscription.id
                )[0]

                if stripe_product is None:
                    # If product doesn't exist.
                    return {'error': 'Product is not exist.'}

                # Insert new tracked times instances
                updated_count = self._save_tracked_time_instance(
                    tracking_time_data, stripe_subscription, solution_booking, user
                )

                total_tracked_time = TimeTrackedDay.objects.filter(
                    solution_booking=solution_booking,
                    date__gte=stripe_subscription.current_period_start,
                    date__lte=stripe_subscription.current_period_end,
                ).aggregate(Sum('tracked_hours'))
                if (total_tracked_time['tracked_hours__sum'] is not None) and (
                    updated_count != 0
                ):
                    # Report to the Stripe
                    idempotency_key = uuid.uuid4()
                    stripe.SubscriptionItem.create_usage_record(
                        stripe_subscription_item.id,
                        quantity=int(total_tracked_time['tracked_hours__sum']),
                        timestamp=int(
                            datetime.datetime.now(datetime.timezone.utc).timestamp()
                        ),
                        action='set',
                        idempotency_key=str(
                            idempotency_key,
                        ),
                    )

                    booking_trackings_queryset = TimeTrackedDay.objects.filter(
                        solution_booking=solution_booking,
                        date__gte=stripe_subscription.current_period_start,
                        date__lte=stripe_subscription.current_period_end,
                    )
                    booking_trackings_serializer = TimeTrackedDaySerializer(
                        booking_trackings_queryset, many=True
                    )

                    return {
                        'tracking_times': booking_trackings_serializer.data,
                    }
                else:
                    return {'error': 'Check your data again.'}

            except SolutionBooking.DoesNotExist:
                # If solution booking doesn't exist.
                return {'error': 'Contract is not exist.'}
        else:
            return {'error': 'Contract is not exist.'}

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['get'])
    def bookings(self, request, *args, **kwargs):
        """
        If the user wants to get solution bookings list:
        http://127.0.0.1:8000/users/bookings/
        http://127.0.0.1:8000/users/bookings/?id=<solution_booking_id>
        """
        user = self.request.user
        contract_id = request.GET.get('id', '')
        context_serializer = {'request': request}
        if contract_id:
            solution_booking_queryset = SolutionBooking.objects.filter(
                booked_by__username=user.username, id=contract_id
            )
        else:
            solution_booking_queryset = SolutionBooking.objects.filter(
                booked_by__username=user.username
            )

        solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
            solution_booking_queryset, context=context_serializer, many=True
        )

        return Response(solution_booking_serializer.data)

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def attach_card(self, request, *args, **kwargs):
        if request.data.get('payment_method'):
            user = self.request.user
            payment_method = request.data.get('payment_method')
            return_data = self._attach_payment_method_to_loggin_user(
                user, payment_method
            )

            return Response(return_data)
        else:
            return Response(
                data={"detail": "incorrect payment method"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, permission_classes=[AllowAny], methods=['get'])
    def payment_methods(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            customer_id = request.query_params.get('customer_id', '')
            if customer_id:
                customer = PartnerCustomer.objects.get(customer_id=customer_id)
                stripe_customer = customer.stripe_customer
                if stripe_customer is None:
                    return Response({'has_payment_method': None})
            else:
                return Response({'has_payment_method': None})
        else:
            stripe_customer = user.stripe_customer
            if stripe_customer is None:
                return Response({'has_payment_method': None})

        customer_payment_methods = stripe.PaymentMethod.list(
            customer=stripe_customer.id,
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
                    "default_payment_method": stripe_customer.default_payment_method.id
                    == payment_method.id,
                }
            )
        return Response(
            {
                'has_payment_method': stripe_customer.default_payment_method
                is not None,
                'payment_methods': return_payment_methods,
            }
        )

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def subscribe_solution(self, request, *args, **kwargs):
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
                    solution_booking = SolutionBooking.objects.create(
                        booked_by=request.user,
                        solution=solution,
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
            try:
                solution_booking = SolutionBooking.objects.get(id=contract_id)
                booking_trackings_queryset = TimeTrackedDay.objects.filter(
                    solution_booking=solution_booking
                )
                booking_trackings_serializer = TimeTrackedDaySerializer(
                    booking_trackings_queryset, many=True
                )
                solution_booking_queryset = SolutionBooking.objects.get(
                    solution__point_of_contact__username=kwargs['username'],
                    id=contract_id,
                )
                solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
                    solution_booking_queryset, context=context_serializer
                )
                stripe_subscription = solution_booking.stripe_subscription
                if stripe_subscription is not None:
                    return Response(
                        {
                            'current_period_start': stripe_subscription.current_period_start,
                            'current_period_end': stripe_subscription.current_period_end,
                            'tracking_times': booking_trackings_serializer.data,
                            'booking_data': solution_booking_serializer.data,
                        }
                    )
                else:
                    return Response({'booking_data': solution_booking_serializer.data})

            except SolutionBooking.DoesNotExist:
                return Response(status=400)
        else:
            solution_booking_queryset = SolutionBooking.objects.filter(
                solution__point_of_contact__username=kwargs['username']
            )

            solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
                solution_booking_queryset, context=context_serializer, many=True
            )

            return Response(solution_booking_serializer.data)

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def tracking_time_report(self, request, *args, **kwargs):
        user = self.request.user
        tracking_time_data = request.data.get('tracking_time')
        contract_id = request.data.get('booking_id', '')
        return_data = self._save_tracked_times(contract_id, tracking_time_data, user)

        return Response(return_data)

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def read_tracking_time_google_sheet_data(self, request, *args, **kwargs):
        user = self.request.user
        google_sheet_url = request.data.get('google_sheet')
        contract_id = request.data.get('booking_id', '')
        read_google_sheet_url = google_sheet_url.replace(
            '/edit#gid=', '/export?format=csv&gid='
        )
        sheet_data = pd.read_csv(read_google_sheet_url)
        count_row = sheet_data.shape[0]
        tracked_data = []
        for iteration in range(0, count_row):
            try:
                tracked_data.append(
                    {
                        'date': sheet_data.iloc[iteration].Date + 'T23:59:59Z',
                        'tracked_hours': sheet_data.iloc[iteration].Hours,
                    }
                )
            except Exception:
                self._save_tracked_times(contract_id, tracked_data, user)
        return_data = self._save_tracked_times(contract_id, tracked_data, user)

        return Response(return_data)

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def start_contract(self, request, *args, **kwargs):
        context_serializer = {'request': request}
        contract_id = request.data.get('booking_id', '')
        username = request.data.get('username', '')
        if contract_id:
            solution_booking = SolutionBooking.objects.get(id=contract_id)
            customer = solution_booking.booked_by
            solution = solution_booking.solution
            stripe_subscription = stripe.Subscription.create(
                customer=customer.stripe_customer.id,
                items=[{'price': solution.stripe_primary_price.id}],
                expand=['latest_invoice.payment_intent'],
            )
            djstripe_subscription = StripeSubscription.sync_from_stripe_data(
                stripe_subscription
            )
            solution_booking.stripe_subscription = djstripe_subscription
            solution_booking.status = SolutionBooking.Status.IN_PROGRESS
            solution_booking.save()

            contract_data = self._get_provider_booking_detail_data(
                contract_id, username, context_serializer
            )

            return Response(contract_data)
        else:
            return Response({'error': 'Contract does not exist.'})

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def pause_or_resume_contract(self, request, *args, **kwargs):
        user = self.request.user
        contract_id = request.data.get('booking_id', '')
        username = request.data.get('username', '')
        context_serializer = {'request': request}
        pause_status = request.data.get('pause_status', None)
        page_type = request.data.get('page_type')
        if contract_id:
            try:
                solution_booking = SolutionBooking.objects.get(id=contract_id)
                solution_booking.pause_status = pause_status
                if pause_status is None:
                    solution_booking.status = SolutionBooking.Status.IN_PROGRESS
                    pause_collection = ''
                else:
                    solution_booking.status = SolutionBooking.Status.PAUSED
                    pause_collection = {'behavior': 'void'}

                stripe_subscription = stripe.Subscription.modify(
                    solution_booking.stripe_subscription.id,
                    pause_collection=pause_collection,
                )
                StripeSubscription.sync_from_stripe_data(stripe_subscription)
                solution_booking.save()
                if page_type == 'provider':
                    contract_data = self._get_provider_booking_detail_data(
                        contract_id, username, context_serializer
                    )
                    return Response(contract_data)
                elif page_type == 'customer':
                    solution_booking_queryset = SolutionBooking.objects.filter(
                        booked_by__username=user.username, id=contract_id
                    )
                    solution_booking_serializer = (
                        AuthenticatedSolutionBookingSerializer(
                            solution_booking_queryset,
                            context=context_serializer,
                            many=True,
                        )
                    )
                    return Response(solution_booking_serializer.data)

            except Exception:
                return Response({'error': 'Contract does not exist.'})
        else:
            return Response({'error': 'Please check your data again.'})

    @action(detail=False, permission_classes=[AllowAny], methods=['post'])
    def attach_card_for_partners(self, request, *args, **kwargs):
        if request.data.get('payment_method'):
            user = self.request.user
            payment_method = request.data.get('payment_method')
            if user.is_anonymous:
                customer_id = request.data.get('customer_id')

                customer, is_created = PartnerCustomer.objects.get_or_create(
                    customer_id=customer_id,
                )

                if customer.stripe_customer is None:
                    stripe_customer = stripe.Customer.create(
                        email=payment_method['billing_details']['email'],
                        name=payment_method['billing_details']['name'],
                    )
                    djstripe_customer = StripeCustomer.sync_from_stripe_data(
                        stripe_customer
                    )
                    customer.stripe_customer = djstripe_customer
                    customer.save()
                else:
                    stripe_customer = customer.stripe_customer

                return_data = self._attach_payment_method_to_stripe_customer(
                    payment_method['id'], stripe_customer
                )

                return Response(return_data)
            else:
                return_data = self._attach_payment_method_to_loggin_user(
                    user, payment_method
                )

                return Response(return_data)
        else:
            return Response(
                data={"detail": "incorrect payment method"},
                status=status.HTTP_400_BAD_REQUEST,
            )
