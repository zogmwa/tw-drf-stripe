import pytest
from django.test import override_settings
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_201_CREATED
from api.models import ThirdPartyCustomer
from api.models.asset_price_plan import AssetPricePlan
from api.models.third_party_customer_session import ThirdPartyCustomerSession
from djstripe.models import Price as StripePrice
from djstripe.models import Product as StripeProduct
from stripe import util

THIRD_PARTY_CUSTOMER_ENDPOINT = 'http://127.0.0.1:8000/third_party_customers/'
ASSET_SUBSCRIPTION_USAGE = 'http://127.0.0.1:8000/asset_subscription_usage/'
THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT = (
    'http://127.0.0.1:8000/third_party_customer_sessions/'
)
FAKE_THIRD_PARTY_CUSTOMER_UID = 'sadsaedasdsa'


class TestThirdPartyCustomer:
    def _generate_session_id(
        self,
        partner,
        stripe_customer_object,
        stripe_price_create_event,
        asset_price_plan_stripe_subscription_object,
        asset,
        pytest_mocker,
    ):
        self._create_stripe_customer(stripe_customer_object, partner, pytest_mocker)
        example_price_data = stripe_price_create_event.data['object']
        example_price_data['id'] = asset_price_plan_stripe_subscription_object['items'][
            'data'
        ][0]['price']['id']
        example_product = StripeProduct.objects.create(
            id=asset_price_plan_stripe_subscription_object['items']['data'][0]['price'][
                'product'
            ],
            name='test codemesh product',
            type='service',
        )
        example_price = StripePrice.objects.create(
            id=example_price_data['id'],
            product=example_product,
            currency=example_price_data['currency'],
            type='Recurring',
            active=True,
        )
        example_asset_price_plan = AssetPricePlan.objects.create(
            asset=asset, name='test price', stripe_price=example_price
        )

        response = partner.post(
            '{}{}/'.format(
                THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT, 'generate_session_url'
            ),
            {
                'action': 'add-payment-method',
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'price_plan_id': example_asset_price_plan.id,
            },
            content_type='application/json',
        )

        return response

    def _create_stripe_customer(self, example_stripe_customer, partner, pytest_mocker):
        test_email = 'test@example.com'
        example_stripe_customer['email'] = test_email

        pytest_mocker.patch(
            'stripe.Customer.create',
            return_value=util.convert_to_stripe_object(example_stripe_customer),
        )

        response = partner.post(
            THIRD_PARTY_CUSTOMER_ENDPOINT,
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'customer_email': test_email,
            },
            content_type='application/json',
        )

        return response

    def _attach_payment_method_to_customer(
        self,
        auth_user,
        unauth_user,
        stripe_customer_object,
        stripe_attach_payment_method_customer_object,
        stripe_customer_has_default_payment_method_object,
        pytest_mocker,
    ):
        stripe_customer_object['name'] = 'Test user'
        pytest_mocker.patch(
            'stripe.Customer.modify',
            return_value=util.convert_to_stripe_object(stripe_customer_object),
        )
        pytest_mocker.patch(
            'stripe.PaymentMethod.retrieve',
            return_value=util.convert_to_stripe_object(
                stripe_attach_payment_method_customer_object
            ),
        )
        pytest_mocker.patch(
            'stripe.PaymentMethod.list',
            return_value={
                "object": "list",
                "url": "/v1/payment_methods",
                "has_more": False,
                'data': [],
            },
        )
        pytest_mocker.patch(
            'stripe.PaymentMethod.attach',
            return_value=util.convert_to_stripe_object(
                stripe_attach_payment_method_customer_object
            ),
        )
        pytest_mocker.patch(
            'stripe.Customer.modify',
            return_value=util.convert_to_stripe_object(
                stripe_customer_has_default_payment_method_object
            ),
        )

        third_party_customer_session = ThirdPartyCustomerSession.objects.get()
        response = unauth_user.post(
            '{}{}/'.format(
                THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT, 'attach_card_for_partners'
            ),
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'session_id': third_party_customer_session.session_id,
                'payment_method': {
                    "id": stripe_attach_payment_method_customer_object['id'],
                    "billing_details": {
                        "name": "Test customer",
                    },
                },
            },
            content_type='application/json',
        )

        return response

    def _subscribe_asset_price_plan(
        self, asset_price_plan_stripe_subscription_object, unauth_user, pytest_mocker
    ):
        pytest_mocker.patch(
            'stripe.Subscription.create',
            return_value=util.convert_to_stripe_object(
                asset_price_plan_stripe_subscription_object
            ),
        )

        third_party_customer_session = ThirdPartyCustomerSession.objects.get()
        asset_price_plan = AssetPricePlan.objects.get()
        response = unauth_user.post(
            '{}{}/'.format(
                THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT,
                'subscribe_customer_to_price_plan',
            ),
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'price_plan_id': asset_price_plan.id,
                'session_id': third_party_customer_session.session_id,
            },
            content_type='application/json',
        )

        return response

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_create_with_logged_in_user(
        self,
        authenticated_client,
        mocker,
        example_stripe_customer_object,
    ):
        response = self._create_stripe_customer(
            example_stripe_customer_object, authenticated_client, mocker
        )

        assert response.status_code == HTTP_201_CREATED
        third_party_customer = ThirdPartyCustomer.objects.get()
        assert third_party_customer.customer_uid == FAKE_THIRD_PARTY_CUSTOMER_UID

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_create_session_url_with_logged_in_user(
        self,
        example_asset,
        example_asset_price_plan_stripe_subscription_object,
        example_stripe_customer_object,
        example_stripe_price_create_event,
        authenticated_client,
        mocker,
    ):
        response = self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )

        assert response.status_code == 200
        assert response.data['url'] is not None

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_third_party_customer_could_attach_payment_method(
        self,
        authenticated_client,
        unauthenticated_client,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_customer_has_default_payment_method_object,
        example_stripe_price_create_event,
        example_asset_price_plan_stripe_subscription_object,
        example_asset,
        example_stripe_customer_object,
        mocker,
    ):
        self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )

        response = self._attach_payment_method_to_customer(
            authenticated_client,
            unauthenticated_client,
            example_stripe_customer_object,
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_has_default_payment_method_object,
            mocker,
        )

        assert response.status_code == 200
        assert response.data['status'] == 'payment method associated successfully'

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_third_party_customer_could_be_retrieve_payment_methods_list(
        self,
        authenticated_client,
        unauthenticated_client,
        example_stripe_customer_object,
        example_stripe_price_create_event,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_attach_payment_method_customer_object_2,
        example_stripe_customer_has_default_payment_method_object,
        example_asset_price_plan_stripe_subscription_object,
        example_asset,
        mocker,
    ):
        self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )

        self._attach_payment_method_to_customer(
            authenticated_client,
            unauthenticated_client,
            example_stripe_customer_object,
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_has_default_payment_method_object,
            mocker,
        )

        mocker.patch(
            'stripe.PaymentMethod.list',
            return_value={
                "object": "list",
                "url": "/v1/payment_methods",
                "has_more": False,
                'data': [
                    util.convert_to_stripe_object(
                        example_stripe_attach_payment_method_customer_object_1
                    ),
                ],
            },
        )
        third_party_customer_session = ThirdPartyCustomerSession.objects.get()
        response = unauthenticated_client.post(
            '{}{}/'.format(
                THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT,
                'payment_methods',
            ),
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'session_id': third_party_customer_session.session_id,
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.data['has_payment_method'] is True
        assert (
            response.data['payment_methods'][0]['id']
            == example_stripe_attach_payment_method_customer_object_1['id']
        )

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_third_party_customer_could_detach_payment_method(
        self,
        authenticated_client,
        unauthenticated_client,
        example_stripe_customer_object,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_attach_payment_method_customer_object_2,
        example_stripe_customer_has_default_payment_method_object,
        example_stripe_customer_has_not_default_payment_method_object,
        example_stripe_detach_payment_method_customer_object_1,
        example_stripe_price_create_event,
        example_asset_price_plan_stripe_subscription_object,
        example_asset,
        mocker,
    ):
        self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )
        mocker.patch(
            'stripe.PaymentMethod.detach',
            return_value=util.convert_to_stripe_object(
                example_stripe_detach_payment_method_customer_object_1
            ),
        )
        mocker.patch(
            'stripe.PaymentMethod.list',
            return_value={
                "object": "list",
                "url": "/v1/payment_methods",
                "has_more": False,
                'data': [],
            },
        )
        mocker.patch(
            'stripe.Customer.modify',
            return_value=util.convert_to_stripe_object(
                example_stripe_customer_has_not_default_payment_method_object
            ),
        )
        self._attach_payment_method_to_customer(
            authenticated_client,
            unauthenticated_client,
            example_stripe_customer_object,
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_has_default_payment_method_object,
            mocker,
        )

        third_party_customer_session = ThirdPartyCustomerSession.objects.get()
        response = authenticated_client.post(
            '{}{}/'.format(
                THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT, 'detach_payment_method'
            ),
            {
                'payment_method': example_stripe_attach_payment_method_customer_object_1[
                    'id'
                ],
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'session_id': third_party_customer_session.session_id,
            },
            content_type='application/json',
        )

        assert response.status_code == 200

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_third_party_customer_could_subscribe_asset_price_plan(
        self,
        authenticated_client,
        unauthenticated_client,
        example_asset,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_customer_has_default_payment_method_object,
        example_asset_price_plan_stripe_subscription_object,
        example_stripe_price_create_event,
        example_stripe_customer_object,
        mocker,
    ):
        self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )

        self._attach_payment_method_to_customer(
            authenticated_client,
            unauthenticated_client,
            example_stripe_customer_object,
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_has_default_payment_method_object,
            mocker,
        )

        response = self._subscribe_asset_price_plan(
            example_asset_price_plan_stripe_subscription_object,
            unauthenticated_client,
            mocker,
        )

        assert response.status_code == 200
        assert response.data['status'] == 'Successfully subscribed'

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_partner_could_report_the_usage_counts(
        self,
        authenticated_client,
        unauthenticated_client,
        example_asset,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_customer_has_default_payment_method_object,
        example_asset_price_plan_stripe_subscription_object,
        example_stripe_price_create_event,
        example_stripe_customer_object,
        example_stripe_usage_object,
        mocker,
    ):
        self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )

        self._attach_payment_method_to_customer(
            authenticated_client,
            unauthenticated_client,
            example_stripe_customer_object,
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_has_default_payment_method_object,
            mocker,
        )

        self._subscribe_asset_price_plan(
            example_asset_price_plan_stripe_subscription_object,
            unauthenticated_client,
            mocker,
        )

        example_stripe_usage_object['quantity'] = 5
        mocker.patch(
            'stripe.SubscriptionItem.create_usage_record',
            return_value=util.convert_to_stripe_object(example_stripe_usage_object),
        )
        asset_price_plan = AssetPricePlan.objects.get()
        response = authenticated_client.post(
            ASSET_SUBSCRIPTION_USAGE,
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'tracked_units': example_stripe_usage_object['quantity'],
                'usage_effective_date': '2022-02-16 00:00:00',
                'price_plan_id': asset_price_plan.id,
            },
            content_type='application/json',
        )

        assert response.status_code == 201
        assert response.data['customer_uid'] == FAKE_THIRD_PARTY_CUSTOMER_UID
        assert response.data['tracked_units'] == example_stripe_usage_object['quantity']

        # usage_effective_date could be a optional.
        response = authenticated_client.post(
            ASSET_SUBSCRIPTION_USAGE,
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'tracked_units': example_stripe_usage_object['quantity'],
                'price_plan_id': asset_price_plan.id,
            },
            content_type='application/json',
        )

        assert response.status_code == 201
        assert response.data['customer_uid'] == FAKE_THIRD_PARTY_CUSTOMER_UID
        assert response.data['usage_effective_date'] is not None

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_third_party_customer_could_cancel_asset_subscription(
        self,
        authenticated_client,
        unauthenticated_client,
        example_asset,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_customer_has_default_payment_method_object,
        example_stripe_subscription_object,
        example_asset_price_plan_stripe_subscription_object,
        example_stripe_price_create_event,
        example_stripe_customer_object,
        mocker,
    ):
        self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )

        self._attach_payment_method_to_customer(
            authenticated_client,
            unauthenticated_client,
            example_stripe_customer_object,
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_has_default_payment_method_object,
            mocker,
        )

        self._subscribe_asset_price_plan(
            example_asset_price_plan_stripe_subscription_object,
            unauthenticated_client,
            mocker,
        )

        example_stripe_subscription_object['cancel_at_period_end'] = True
        mocker.patch(
            'stripe.Subscription.modify',
            return_value=util.convert_to_stripe_object(
                example_stripe_subscription_object
            ),
        )
        asset_price_plan = AssetPricePlan.objects.get()
        response = authenticated_client.post(
            '{}{}/'.format(
                THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT,
                'cancel_asset_subscription_by_partner',
            ),
            {
                'price_plan_id': asset_price_plan.id,
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.data['status'] == 'successfully canceled.'

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_partner_should_pause_or_resume_subscription(
        self,
        user_and_password,
        authenticated_client,
        unauthenticated_client,
        example_stripe_price_create_event,
        example_stripe_customer_object,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_customer_has_default_payment_method_object,
        example_asset_price_plan_stripe_subscription_object,
        example_stripe_subscription_pause_object,
        example_stripe_subscription_resume_object,
        example_asset,
        mocker,
    ):
        self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )

        self._attach_payment_method_to_customer(
            authenticated_client,
            unauthenticated_client,
            example_stripe_customer_object,
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_has_default_payment_method_object,
            mocker,
        )

        self._subscribe_asset_price_plan(
            example_asset_price_plan_stripe_subscription_object,
            unauthenticated_client,
            mocker,
        )

        mocker.patch(
            'stripe.Subscription.modify',
            return_value=util.convert_to_stripe_object(
                example_stripe_subscription_pause_object
            ),
        )

        # Pause the subscription
        asset_price_plan = AssetPricePlan.objects.get()
        response = authenticated_client.post(
            '{}{}/'.format(
                THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT,
                'pause_or_resume_asset_subscription',
            ),
            {
                'price_plan_id': asset_price_plan.id,
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'pause_status': 'pause',
            },
            content_type='application/json',
        )

        response.status_code == 200
        response.data['status'] == 'subscription paused'

        mocker.patch(
            'stripe.Subscription.modify',
            return_value=util.convert_to_stripe_object(
                example_stripe_subscription_resume_object
            ),
        )

        # Resume the subscription
        response = authenticated_client.post(
            '{}{}/'.format(
                THIRD_PARTY_CUSTOMER_SESSION_ENDPOINT,
                'pause_or_resume_asset_subscription',
            ),
            {
                'price_plan_id': asset_price_plan.id,
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'pause_status': 'resume',
            },
            content_type='application/json',
        )

        response.status_code == 200
        response.data['status'] == 'subscription resumed'

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_partner_could_fetch_customers_payment_method_count(
        self,
        authenticated_client,
        unauthenticated_client,
        example_stripe_customer_object,
        example_stripe_price_create_event,
        example_asset_price_plan_stripe_subscription_object,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_customer_has_default_payment_method_object,
        example_asset,
        mocker,
    ):
        self._generate_session_id(
            authenticated_client,
            example_stripe_customer_object,
            example_stripe_price_create_event,
            example_asset_price_plan_stripe_subscription_object,
            example_asset,
            mocker,
        )

        mocker.patch(
            'stripe.PaymentMethod.list',
            return_value={
                "object": "list",
                "url": "/v1/payment_methods",
                "has_more": False,
                'data': [],
            },
        )

        response = authenticated_client.get(
            '{}{}/?{}={}'.format(
                THIRD_PARTY_CUSTOMER_ENDPOINT,
                'customer_payment_methods_count',
                'customer_uid',
                FAKE_THIRD_PARTY_CUSTOMER_UID,
            )
        )

        assert response.status_code == 200
        assert response.data['payment_methods'] == 0

        self._attach_payment_method_to_customer(
            authenticated_client,
            unauthenticated_client,
            example_stripe_customer_object,
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_has_default_payment_method_object,
            mocker,
        )

        mocker.patch(
            'stripe.PaymentMethod.list',
            return_value={
                "object": "list",
                "url": "/v1/payment_methods",
                "has_more": False,
                'data': [
                    util.convert_to_stripe_object(
                        example_stripe_attach_payment_method_customer_object_1
                    ),
                ],
            },
        )

        response = authenticated_client.get(
            '{}{}/?{}={}'.format(
                THIRD_PARTY_CUSTOMER_ENDPOINT,
                'customer_payment_methods_count',
                'customer_uid',
                FAKE_THIRD_PARTY_CUSTOMER_UID,
            )
        )

        assert response.status_code == 200
        assert response.data['payment_methods'] == 1
