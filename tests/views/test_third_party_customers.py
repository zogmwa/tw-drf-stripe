import pytest
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_201_CREATED

from api.models import ThirdPartyCustomer
from api.serializers.third_pary_customer import ThirdPartyCustomerSerializer

THIRD_PARTY_CUSTOMER_ENDPOINT = 'http://127.0.0.1:8000/third_party_customers/'


class TestThirdPartyCustomer:
    def test_create_with_logged_in_user(
        self,
        authenticated_client,
        user_and_password,
        mocker,
        example_stripe_customer_object,
    ):
        test_email = 'test@example.com'
        example_stripe_customer_object['email'] = 'test@example.com'

        mocker.patch.object(
            ThirdPartyCustomerSerializer,
            '_stripe_customer_create',
            return_value=example_stripe_customer_object,
        )
        fake_third_party_customer_uid = 'sadsaedasdsa'
        # Vote on asset attribute
        response = authenticated_client.post(
            THIRD_PARTY_CUSTOMER_ENDPOINT,
            {
                'customer_uid': fake_third_party_customer_uid,
                # TODO: Uncomment this when the logic to mock stripe.Customer.create is added to the tests
                'customer_email': test_email,
            },
        )
        assert response.status_code == HTTP_201_CREATED
        third_party_customer = ThirdPartyCustomer.objects.get()
        assert third_party_customer.customer_uid == fake_third_party_customer_uid
