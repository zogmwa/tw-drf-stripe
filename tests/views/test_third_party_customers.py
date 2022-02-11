import pytest
from django.test import override_settings
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_201_CREATED

from api.models import ThirdPartyCustomer
from stripe import util
from api.serializers.third_pary_customer import ThirdPartyCustomerSerializer

THIRD_PARTY_CUSTOMER_ENDPOINT = 'http://127.0.0.1:8000/third_party_customers/'


class TestThirdPartyCustomer:
    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_create_with_logged_in_user(
        self,
        authenticated_client,
        user_and_password,
        mocker,
        example_stripe_customer_object,
    ):
        test_email = 'test@example.com'
        example_stripe_customer_object['email'] = test_email

        mocker.patch(
            'stripe.Customer.create',
            return_value=util.convert_to_stripe_object(example_stripe_customer_object),
        )
        fake_third_party_customer_uid = 'sadsaedasdsa'
        # Vote on asset attribute
        response = authenticated_client.post(
            THIRD_PARTY_CUSTOMER_ENDPOINT,
            {
                'customer_uid': fake_third_party_customer_uid,
                'customer_email': test_email,
            },
        )
        assert response.status_code == HTTP_201_CREATED
        third_party_customer = ThirdPartyCustomer.objects.get()
        assert third_party_customer.customer_uid == fake_third_party_customer_uid
