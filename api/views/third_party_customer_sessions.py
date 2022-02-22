import stripe
from furl import furl
from datetime import datetime, timedelta
from django.conf import settings
from api.utils.models import get_or_none
from rest_framework import permissions, viewsets, status
from dateutil.relativedelta import relativedelta
from api.permissions.user_permissions import AllowOnlyThirdPartyCustomers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.sites.models import Site
from djstripe.models import Customer as StripeCustomer
from api.models import ThirdPartyCustomer, ThirdPartyCustomerSession
from api.models.asset_price_plan_subscription import AssetPricePlanSubscription
from djstripe.models import Subscription as StripeSubscription
from api.models.asset_price_plan import AssetPricePlan
from api.views.user import UserViewSet

REQUEST_ACTIONS = [
    'add-payment-method',
    'start-plan-subscription',
]


class ThirdPartyCustomerSessionViewSet(viewsets.ModelViewSet):
    queryset = ThirdPartyCustomerSession.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def _check_valid_session_id(session_id, customer_uid):
        try:
            third_party_customer_session = ThirdPartyCustomerSession.objects.get(
                session_id=session_id, third_party_customer__customer_uid=customer_uid
            )
            if (
                third_party_customer_session.expiration_time.replace(tzinfo=None)
                > datetime.now()
            ) and (third_party_customer_session.is_expired is False):
                return True
            else:
                return False
        except ThirdPartyCustomerSession.DoesNotExist:
            return False

    @staticmethod
    def _check_validation_data(customer_uid, asset_price_plan_id, user):
        try:
            partner_customer = ThirdPartyCustomer.objects.get(
                customer_uid=customer_uid, organization=user.organization
            )
            asset_price_plan_subscription = AssetPricePlanSubscription.objects.get(
                customer=partner_customer, price_plan__id=asset_price_plan_id
            )
            return {"status": True, "data": asset_price_plan_subscription}
        except ThirdPartyCustomer.DoesNotExist:
            return {"status": False, "data": {"detail": "customer does not exist"}}
        except AssetPricePlanSubscription.DoesNotExist:
            return {
                "status": False,
                "data": {"detail": "asset price plan subscription does not exist"},
            }

    @action(
        detail=False, permission_classes=[permissions.IsAuthenticated], methods=['post']
    )
    def generate_session_url(self, request, *args, **kwargs):
        """ """
        user = self.request.user
        action_type = request.data.get('action', '')
        customer_uid = request.data.get('customer_uid', '')
        price_plan_id = request.data.get('price_plan_id', '')

        if user.organization:
            if action_type in REQUEST_ACTIONS:
                try:
                    third_party_customer = ThirdPartyCustomer.objects.get(
                        customer_uid=customer_uid, organization=user.organization
                    )
                    expiration_time = datetime.now() + timedelta(
                        seconds=settings.THIRD_PATRY_SESSION_EXPIRE_DURATION
                    )
                    third_party_customer_session = (
                        ThirdPartyCustomerSession.objects.create(
                            third_party_customer=third_party_customer,
                            expiration_time=expiration_time,
                        )
                    )
                    asset_price_plan = AssetPricePlan.objects.get(id=price_plan_id)

                    active_site_obj = Site.objects.get(id=settings.SITE_ID)
                    active_site = furl('https://{}'.format(active_site_obj.domain))
                    return_url = '{}/{}/{}/{}/{}/{}?session_id={}'.format(
                        active_site,
                        'partners',
                        user.organization.name,
                        asset_price_plan.id,
                        customer_uid,
                        action_type,
                        third_party_customer_session.session_id,
                    )
                    return Response({'url': return_url})
                except ThirdPartyCustomer.DoesNotExist:
                    return Response(
                        data={"detail": "Third party customer doesn't exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                except AssetPricePlan.DoesNotExist:
                    return Response(
                        data={"detail": "Asset price plan doesn't exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    data={
                        "detail": "Unknown request action.",
                        "action_lists": REQUEST_ACTIONS,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                data={
                    "detail": "User organization is not set, please contact a TaggedWeb admin and they will help you"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        permission_classes=[AllowOnlyThirdPartyCustomers],
        methods=['post'],
    )
    def partner_price_plan(self, request, *args, **kwargs):
        customer_uid = request.data.get('customer_uid', '')
        session_id = request.data.get('session_id', '')
        if self._check_valid_session_id(session_id, customer_uid):
            asset_price_plan_id = request.data.get('price_id')
            customer = get_or_none(ThirdPartyCustomer, customer_uid=customer_uid)
            asset_price_plan = get_or_none(AssetPricePlan, id=asset_price_plan_id)

            if (customer is None) or (asset_price_plan is None):
                return Response({'status: None data'})

            return Response(
                {
                    'email': customer.stripe_customer.email,
                    'organization': {
                        'name': customer.organization.name,
                        'logo_url': customer.organization.logo_url,
                        'website': customer.organization.website,
                    },
                    'price_plan': {
                        'name': asset_price_plan.name,
                        'price': asset_price_plan.price,
                        'per': asset_price_plan.per,
                        'currency': asset_price_plan.currency,
                        'asset': {
                            'name': asset_price_plan.asset.name,
                            'slug': asset_price_plan.asset.slug,
                        },
                    },
                }
            )
        else:
            return Response({'status': 'None data'})

    @action(
        detail=False,
        permission_classes=[AllowOnlyThirdPartyCustomers],
        methods=['post'],
    )
    def attach_card_for_partners(self, request, *args, **kwargs):
        session_id = request.data.get('session_id', '')
        customer_uid = request.data.get('customer_uid')
        if self._check_valid_session_id(session_id, customer_uid):
            if request.data.get('payment_method'):
                payment_method = request.data.get('payment_method')

                third_party_customer = get_or_none(
                    ThirdPartyCustomer, customer_uid=customer_uid
                )

                if third_party_customer is not None:
                    stripe_customer = stripe.Customer.modify(
                        third_party_customer.stripe_customer.id,
                        name=payment_method['billing_details']['name'],
                    )
                    djstripe_customer = StripeCustomer.sync_from_stripe_data(
                        stripe_customer
                    )
                    third_party_customer.stripe_customer = djstripe_customer
                    third_party_customer.save()

                    return_data = UserViewSet._attach_payment_method_to_stripe_customer(
                        payment_method['id'], stripe_customer
                    )

                    return Response(return_data)
                else:
                    return Response(
                        data={"detail": "incorrect payment method"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    data={"detail": "incorrect payment method"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                data={"detail": "invalid session data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        permission_classes=[AllowOnlyThirdPartyCustomers],
        methods=['post'],
    )
    def detach_payment_method(self, request, *args, **kwargs):
        session_id = request.data.get('session_id', '')
        customer_uid = request.data.get('customer_uid', '')
        if self._check_valid_session_id(session_id, customer_uid):
            try:
                if customer_uid:
                    third_party_customer = ThirdPartyCustomer.objects.get(
                        customer_uid=customer_uid
                    )
                    stripe_customer = third_party_customer.stripe_customer
                    return_data = (
                        UserViewSet._detach_payment_method_from_stripe_customer(
                            request.data.get('payment_method'), stripe_customer
                        )
                    )

                    return Response(return_data)
            except ThirdPartyCustomer.DoesNotExist:
                return Response({'has_payment_method': None})
        else:
            return Response(
                data={"detail": "invalid session data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        permission_classes=[AllowOnlyThirdPartyCustomers],
        methods=['post'],
    )
    def payment_methods(self, request, *args, **kwargs):
        session_id = request.data.get('session_id', '')
        customer_uid = request.data.get('customer_uid', '')
        if self._check_valid_session_id(session_id, customer_uid):
            if customer_uid:
                third_party_customer = ThirdPartyCustomer.objects.get(
                    customer_uid=customer_uid
                )
                stripe_customer = third_party_customer.stripe_customer
                if stripe_customer is None:
                    return Response({'has_payment_method': None})

                return_payment_methods = UserViewSet._fetch_payment_methods(
                    stripe_customer
                )
                return Response(
                    {
                        'has_payment_method': stripe_customer.default_payment_method
                        is not None,
                        'payment_methods': return_payment_methods,
                    }
                )

            else:
                return Response({'has_payment_method': None})
        else:
            return Response(
                data={"detail": "invalid session data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        permission_classes=[AllowOnlyThirdPartyCustomers],
        methods=['post'],
    )
    def subscribe_customer_to_price_plan(self, request, *args, **kwargs):
        session_id = request.data.get('session_id', '')
        customer_uid = request.data.get('customer_uid')
        if self._check_valid_session_id(session_id, customer_uid):
            asset_price_plan_id = request.data.get('price_plan_id')
            asset_price_plan = get_or_none(AssetPricePlan, id=asset_price_plan_id)

            partner_customer = get_or_none(
                ThirdPartyCustomer, customer_uid=customer_uid
            )
            if (partner_customer is None) or (asset_price_plan is None):
                return Response(
                    data={"detail": "Customer is not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                stripe_customer = partner_customer.stripe_customer
                asset_booking = AssetPricePlanSubscription.objects.create(
                    customer=partner_customer, price_plan=asset_price_plan
                )

                current_day = datetime.now().day
                if current_day >= 5:
                    billing_cycle_anchor = int(
                        (datetime.now() + relativedelta(months=1, day=5)).timestamp()
                    )
                else:
                    billing_cycle_anchor = int(
                        (datetime.now() + relativedelta(day=5)).timestamp()
                    )

                stripe_subscription = stripe.Subscription.create(
                    customer=stripe_customer.id,
                    items=[{'price': asset_price_plan.stripe_price.id}],
                    expand=['latest_invoice.payment_intent'],
                    billing_cycle_anchor=billing_cycle_anchor,
                )

                djstripe_subscription = StripeSubscription.sync_from_stripe_data(
                    stripe_subscription
                )

                asset_booking.stripe_subscription = djstripe_subscription
                asset_booking.save()

                return Response({'status': 'Successfully subscribed'})
            except AssetPricePlanSubscription.DoesNotExist:
                return Response(
                    data={"detail": "Asset price plan does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                data={"detail": "invalid session data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False, permission_classes=[permissions.IsAuthenticated], methods=['post']
    )
    def cancel_asset_subscription_by_partner(self, request, *args, **kwargs):
        user = self.request.user
        asset_price_plan_id = request.data.get('price_plan_id', '')
        customer_uid = request.data.get('customer_uid', '')
        if user.organization:
            validation_result = self._check_validation_data(
                customer_uid, asset_price_plan_id, user
            )
            if validation_result['status'] is True:
                asset_price_plan_subscription = validation_result['data']
            else:
                return Response(
                    data={"detail": validation_result['data']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            stripe_subscription = stripe.Subscription.modify(
                asset_price_plan_subscription.stripe_subscription.id,
                cancel_at_period_end=True,
            )
            StripeSubscription.sync_from_stripe_data(stripe_subscription)
            asset_price_plan_subscription.delete()
            return Response({'status': 'successfully canceled.'})
        else:
            return Response(
                data={"detail": "partner organization does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False, permission_classes=[permissions.IsAuthenticated], methods=['post']
    )
    def pause_or_resume_asset_subscription(self, request, *args, **kwargs):
        user = self.request.user
        customer_uid = request.data.get('customer_uid', '')
        asset_price_plan_id = request.data.get('price_plan_id', '')
        pause_status = request.data.get('pause_status')
        if user.organization:
            validation_result = self._check_validation_data(
                customer_uid, asset_price_plan_id, user
            )
            if validation_result['status'] is True:
                asset_price_plan_subscription = validation_result['data']
            else:
                return Response(
                    data={"detail": validation_result['data']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if pause_status == 'pause':
                pause_collection = {'behavior': 'void'}
            elif pause_status == 'resume':
                pause_collection = ''
            else:
                return Response(
                    data={"detail": "incorrect pause status."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            stripe_subscription = stripe.Subscription.modify(
                asset_price_plan_subscription.stripe_subscription.id,
                pause_collection=pause_collection,
            )
            """
            This will update the old djstripe Subscription instance attached to the asset_subscription 
            (asset_subscription.stripe_subscription)
            """
            StripeSubscription.sync_from_stripe_data(stripe_subscription)
            if pause_status == 'pause':
                return Response({'status': 'subscription paused'})
            else:
                return Response({'status': 'subscription resumed'})
        else:
            return Response(
                data={
                    "detail": "User organization is not set, please contact a TaggedWeb admin and they will help you"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )