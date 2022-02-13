import pytest
from django.test import override_settings
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_201_CREATED

from api.models import ThirdPartyCustomer
from api.models.asset_price_plan import AssetPricePlan
from djstripe.models import Price as StripePrice
from djstripe.models import Product as StripeProduct
from stripe import util

THIRD_PARTY_CUSTOMER_ENDPOINT = 'http://127.0.0.1:8000/third_party_customers/'
USERS_BASE_ENDPOINT = 'http://127.0.0.1:8000/users/'
FAKE_THIRD_PARTY_CUSTOMER_UID = 'sadsaedasdsa'


class TestThirdPartyCustomer:
    def _create_stripe_customer(self, example_stripe_customer, partner, mock):
        test_email = 'test@example.com'
        example_stripe_customer['email'] = test_email

        mock.patch(
            'stripe.Customer.create',
            return_value=util.convert_to_stripe_object(example_stripe_customer),
        )

        # Vote on asset attribute
        response = partner.post(
            THIRD_PARTY_CUSTOMER_ENDPOINT,
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'customer_email': test_email,
            },
        )

        return response

    def _attach_payment_method_to_customer(
        self,
        auth_user,
        unauth_user,
        stripe_customer_object,
        stripe_attach_payment_method_customer_object,
        stripe_customer_has_default_payment_method_object,
        mock,
    ):
        self._create_stripe_customer(stripe_customer_object, auth_user, mock)

        stripe_customer_object['name'] = 'Test user'
        mock.patch(
            'stripe.Customer.modify',
            return_value=util.convert_to_stripe_object(stripe_customer_object),
        )
        mock.patch(
            'stripe.PaymentMethod.retrieve',
            return_value=util.convert_to_stripe_object(
                stripe_attach_payment_method_customer_object
            ),
        )
        mock.patch(
            'stripe.PaymentMethod.list',
            return_value={
                "object": "list",
                "url": "/v1/payment_methods",
                "has_more": False,
                'data': [],
            },
        )
        mock.patch(
            'stripe.PaymentMethod.attach',
            return_value=util.convert_to_stripe_object(
                stripe_attach_payment_method_customer_object
            ),
        )
        mock.patch(
            'stripe.Customer.modify',
            return_value=util.convert_to_stripe_object(
                stripe_customer_has_default_payment_method_object
            ),
        )

        response = unauth_user.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'attach_card_for_partners'),
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
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
    def test_third_party_customer_could_attach_payment_method(
        self,
        authenticated_client,
        unauthenticated_client,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_customer_has_default_payment_method_object,
        example_stripe_customer_object,
        mocker,
    ):
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
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_attach_payment_method_customer_object_2,
        example_stripe_customer_has_default_payment_method_object,
        mocker,
    ):
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
        response = unauthenticated_client.get(
            '{}{}/?{}={}'.format(
                USERS_BASE_ENDPOINT,
                'payment_methods',
                'customer_uid',
                FAKE_THIRD_PARTY_CUSTOMER_UID,
            ),
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
        mocker,
    ):
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

        response = authenticated_client.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'detach_payment_method'),
            {
                'payment_method': example_stripe_attach_payment_method_customer_object_1[
                    'id'
                ],
                'partner_customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
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
        example_price_data = example_stripe_price_create_event.data['object']
        example_price_data['id'] = example_asset_price_plan_stripe_subscription_object[
            'items'
        ]['data'][0]['price']['id']
        example_product = StripeProduct.objects.create(
            id=example_asset_price_plan_stripe_subscription_object['items']['data'][0][
                'price'
            ]['product'],
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
            asset=example_asset, name='test price', stripe_price=example_price
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
            'stripe.Subscription.create',
            return_value=util.convert_to_stripe_object(
                example_asset_price_plan_stripe_subscription_object
            ),
        )

        response = unauthenticated_client.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'subscribe_asset_price_plan'),
            {
                'customer_uid': FAKE_THIRD_PARTY_CUSTOMER_UID,
                'price_plan_id': example_asset_price_plan.id,
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.data['status'] == 'Successfully subscribed'
