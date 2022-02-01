import pytest
import string
from allauth.socialaccount.models import SocialApp, SocialAccount
from django.test import Client
from rest_framework import status
from django.test import override_settings
from stripe import util
from api.models import User, Organization, Asset, SolutionBookmark, Solution
from api.models.solution_booking import SolutionBooking
from djstripe.models import Customer as StripeCustomer
from djstripe.models import PaymentMethod as StripePaymentMethod
from djstripe.models import Price as StripePrice
from djstripe.models import Product as StripeProduct
from tests.common import get_random_string
from tests.views.test_asset import _create_asset

USERS_BASE_ENDPOINT = 'http://127.0.0.1:8000/users/'


def _create_social_app(provider_name: string):
    return SocialApp.objects.create(
        provider=provider_name,
        name=get_random_string(10),
        client_id=get_random_string(10),
        secret=get_random_string(10),
        key=get_random_string(10),
    )


def _create_social_account(user_id, provider):
    return SocialAccount.objects.create(
        provider=provider, uid=get_random_string(10), user_id=user_id
    )


class TestSocialAccountsOnUserListAndDetailEndpoint:
    def test_social_accounts_of_users_should_by_passed_in_users_list_and_detail_endpoint(
        self, admin_client, admin_user
    ):
        google = 'Google'
        linkedin = 'Linkedin'
        expected_list = [google, linkedin]
        expected_list.sort()
        _create_social_app(google)
        _create_social_app(linkedin)

        _create_social_account(admin_user.id, google)
        _create_social_account(admin_user.id, linkedin)

        response = admin_client.get(USERS_BASE_ENDPOINT)
        assert response.data[1]['social_accounts'].__len__() == 2
        response_list = response.data[1]['social_accounts']
        response_list.sort()
        assert response_list == expected_list

        response = admin_client.get(
            '{}{}/'.format(USERS_BASE_ENDPOINT, admin_user.username)
        )

        assert response.data['social_accounts'].__len__() == 2
        response_list = response.data['social_accounts']
        response_list.sort()
        assert response_list == expected_list


class TestSubmittedAndPendingAssetsOnUserDetailsEndpoint:
    """
    This is because when a user submits an asset they should be able to visit the details page to view and edit it.
    Regardless of whether the asset is still pending approval.
    """

    @pytest.mark.parametrize('is_published', [True, False])
    def test_user_is_able_to_see_submitted_assets_whether_published_or_not_and_pending_asset_ids_if_not_published(
        self, authenticated_client, user_and_password, is_published
    ):
        asset_create_response = _create_asset(authenticated_client)
        assert asset_create_response.status_code == 201
        expected_asset_id = asset_create_response.data['id']

        expected_asset = Asset.objects.get(id=expected_asset_id)
        expected_asset.is_published = is_published
        expected_asset.save()

        user_profile_url = '{}{}/'.format(
            USERS_BASE_ENDPOINT, user_and_password[0].username
        )

        response = authenticated_client.get(user_profile_url)

        assert response.status_code == 200
        assert len(response.data['submitted_assets']) == 1
        assert response.data['submitted_assets'][0]['id'] == expected_asset_id

        pending_asset_ids = response.data['pending_asset_ids']
        if is_published:
            assert pending_asset_ids == []
        else:
            assert len(pending_asset_ids) == 1
            assert pending_asset_ids[0] == expected_asset_id


class TestUserOrganizationLinking:
    @pytest.fixture
    def example_organization(self):
        return Organization.objects.create(
            name='orgnization1', website='organization1.com'
        )

    def _test_organization_user_link(self, user_name, pk):
        user = User.objects.get(username=user_name)
        assert user.organization.pk == pk

    def test_when_user_and_organization_are_created(
        self, user_and_password, authenticated_client
    ):
        username = 'test_user'
        organization_name = 'organization-name'
        response = authenticated_client.post(
            USERS_BASE_ENDPOINT,
            {'username': username, 'organization': {'name': organization_name}},
            'application/json',
        )

        assert response.status_code == 201
        self._test_organization_user_link(
            username, Organization.objects.get(name=organization_name).id
        )

    def test_when_an_existing_user_is_updated_to_add_a_new_organization(
        self, user_and_password, authenticated_client
    ):
        organization_name = 'organization-name'
        user_update_url = '{}{}/'.format(
            USERS_BASE_ENDPOINT, user_and_password[0].username
        )
        response = authenticated_client.put(
            user_update_url,
            {
                'username': user_and_password[0].username,
                'organization': {'name': organization_name},
            },
            'application/json',
        )

        assert response.status_code == 200
        self._test_organization_user_link(
            user_and_password[0].username,
            Organization.objects.get(name=organization_name).id,
        )

    def test_existing_user_is_updated_by_using_an_existing_organization_suggestion(
        self, user_and_password, authenticated_client, example_organization
    ):
        organization_name = example_organization.name
        user_update_url = '{}{}/'.format(
            USERS_BASE_ENDPOINT, user_and_password[0].username
        )
        response = authenticated_client.put(
            user_update_url,
            {
                'username': user_and_password[0].username,
                'organization': {'name': organization_name},
            },
            'application/json',
        )

        assert response.status_code == 200
        self._test_organization_user_link(
            user_and_password[0].username,
            example_organization.id,
        )

    def test_new_user_is_created_by_using_an_existing_organization_suggestion(
        self, user_and_password, authenticated_client, example_organization
    ):
        username = 'test_user'
        organization_name = example_organization.name
        response = authenticated_client.post(
            USERS_BASE_ENDPOINT,
            {'username': username, 'organization': {'name': organization_name}},
            'application/json',
        )

        assert response.status_code == 201
        self._test_organization_user_link(
            username, Organization.objects.get(name=organization_name).id
        )


class TestUserPayment:
    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def _make_user_customer_with_default_payment_method(
        self,
        user,
        stripe_customer_payment_object,
        stripe_customer_object,
    ):
        example_stripe_payment_method = StripePaymentMethod.objects.create(
            id=stripe_customer_payment_object['id'],
            billing_details=stripe_customer_payment_object['billing_details'],
        )
        example_stripe_customer = StripeCustomer.objects.create(
            id=stripe_customer_object['id'],
            email=user.email,
            default_payment_method=example_stripe_payment_method,
        )
        User.objects.filter(id=user.id).update(stripe_customer=example_stripe_customer)

    def _customer_subscribe_payment(
        self,
        mock,
        stipe_subscription_object,
        price_create_event,
        product_create_event,
        solution_object,
        user,
        customer_attached_mayment,
        auth_client,
        stripe_customer,
    ):
        mock.patch(
            'stripe.Subscription.create',
            return_value=util.convert_to_stripe_object(stipe_subscription_object),
        )
        example_price_data = price_create_event.data['object']
        example_product = StripeProduct.objects.get(
            id=product_create_event.data['object']['id']
        )
        example_price = StripePrice.objects.create(
            id=example_price_data['id'],
            product=example_product,
            currency=example_price_data['currency'],
            type='Recurring',
            active=True,
        )
        solution_object.stripe_primary_price = example_price
        solution_object.save()

        self._make_user_customer_with_default_payment_method(
            user[0],
            customer_attached_mayment,
            stripe_customer,
        )

        response = auth_client.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'subscribe_payment'),
            {
                'payment_method': customer_attached_mayment['id'],
                'slug': solution_object.slug,
            },
            content_type='application/json',
        )

        return response

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_authenticated_user_could_be_create_customer_and_attach_card(
        self,
        authenticated_client,
        example_stripe_customer_object,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_attach_payment_method_customer_object_2,
        example_stripe_customer_has_default_payment_method_object,
        mocker,
    ):
        # Attach first payment to user.
        mocker.patch(
            'stripe.Customer.create',
            return_value=util.convert_to_stripe_object(example_stripe_customer_object),
        )
        mocker.patch(
            'stripe.PaymentMethod.retrieve',
            return_value=util.convert_to_stripe_object(
                example_stripe_attach_payment_method_customer_object_1
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
            'stripe.PaymentMethod.attach',
            return_value=util.convert_to_stripe_object(
                example_stripe_attach_payment_method_customer_object_1
            ),
        )
        mocker.patch(
            'stripe.Customer.modify',
            return_value=util.convert_to_stripe_object(
                example_stripe_customer_has_default_payment_method_object
            ),
        )
        response = authenticated_client.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'attach_card'),
            {
                'payment_method': example_stripe_attach_payment_method_customer_object_1[
                    'id'
                ]
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.data['status'] == 'payment method associated successfully'

        # Attach second payment to user.
        mocker.patch(
            'stripe.PaymentMethod.attach',
            return_value=util.convert_to_stripe_object(
                example_stripe_attach_payment_method_customer_object_2
            ),
        )
        mocker.patch(
            'stripe.PaymentMethod.retrieve',
            return_value=util.convert_to_stripe_object(
                example_stripe_attach_payment_method_customer_object_2
            ),
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
        response = authenticated_client.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'attach_card'),
            {
                'payment_method': example_stripe_attach_payment_method_customer_object_2[
                    'id'
                ]
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.data['status'] == 'payment method associated successfully'

        # Attach same payment to user
        mocker.patch(
            'stripe.PaymentMethod.attach',
            return_value=util.convert_to_stripe_object(
                example_stripe_attach_payment_method_customer_object_2
            ),
        )
        mocker.patch(
            'stripe.PaymentMethod.retrieve',
            return_value=util.convert_to_stripe_object(
                example_stripe_attach_payment_method_customer_object_2
            ),
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
                    util.convert_to_stripe_object(
                        example_stripe_attach_payment_method_customer_object_2
                    ),
                ],
            },
        )
        response = authenticated_client.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'attach_card'),
            {
                'payment_method': example_stripe_attach_payment_method_customer_object_2[
                    'id'
                ]
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.data['status'] == 'You have already attached this payment.'

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_authenticated_user_could_be_retrieve_payment_methods_list(
        self,
        user_and_password,
        authenticated_client,
        example_stripe_customer_object,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_attach_payment_method_customer_object_2,
        example_stripe_customer_has_default_payment_method_object,
        mocker,
    ):
        mocker.patch(
            'stripe.PaymentMethod.retrieve',
            return_value=util.convert_to_stripe_object(
                example_stripe_attach_payment_method_customer_object_2
            ),
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
        mocker.patch(
            'stripe.PaymentMethod.attach',
            return_value=util.convert_to_stripe_object(
                example_stripe_attach_payment_method_customer_object_2
            ),
        )
        self._make_user_customer_with_default_payment_method(
            user_and_password[0],
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_object,
        )

        response = authenticated_client.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'attach_card'),
            {
                'payment_method': example_stripe_attach_payment_method_customer_object_2[
                    'id'
                ]
            },
            content_type='application/json',
        )

        response.status_code == 200

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
                    util.convert_to_stripe_object(
                        example_stripe_attach_payment_method_customer_object_2
                    ),
                ],
            },
        )
        response = authenticated_client.get(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'payment_methods'),
        )

        assert response.status_code == 200
        assert response.data['has_payment_method'] == True
        assert (
            response.data['payment_methods'][0]['id']
            == example_stripe_attach_payment_method_customer_object_1['id']
        )
        assert (
            response.data['payment_methods'][1]['id']
            == example_stripe_attach_payment_method_customer_object_2['id']
        )

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_authenticated_user_could_be_subscribe_using_payment_method(
        self,
        user_and_password,
        authenticated_client,
        example_solution,
        example_stripe_product_create_event,
        example_stripe_price_create_event,
        example_stripe_subscription_object,
        example_stripe_customer_object,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_attach_payment_method_customer_object_2,
        example_stripe_customer_has_default_payment_method_object,
        mocker,
    ):
        response = self._customer_subscribe_payment(
            mocker,
            example_stripe_subscription_object,
            example_stripe_price_create_event,
            example_stripe_product_create_event,
            example_solution,
            user_and_password,
            example_stripe_attach_payment_method_customer_object_1,
            authenticated_client,
            example_stripe_customer_object,
        )

        assert response.status_code == 200
        assert response.data['solution_booking_id'] is not None

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_authenticated_user_could_be_detach_payment_method(
        self,
        user_and_password,
        authenticated_client,
        example_solution,
        example_stripe_customer_object,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_attach_payment_method_customer_object_2,
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
                'data': [
                    util.convert_to_stripe_object(
                        example_stripe_attach_payment_method_customer_object_2
                    ),
                ],
            },
        )
        mocker.patch(
            'stripe.Customer.modify',
            return_value=util.convert_to_stripe_object(
                example_stripe_customer_has_not_default_payment_method_object
            ),
        )
        self._make_user_customer_with_default_payment_method(
            user_and_password[0],
            example_stripe_attach_payment_method_customer_object_1,
            example_stripe_customer_object,
        )

        response = authenticated_client.post(
            '{}{}/'.format(USERS_BASE_ENDPOINT, 'detach_payment_method'),
            {
                'payment_method': example_stripe_attach_payment_method_customer_object_1[
                    'id'
                ],
                'slug': example_solution.slug,
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert (
            response.data['data'][0]['id']
            == example_stripe_attach_payment_method_customer_object_2['id']
        )

    def test_authenticated_user_could_fetch_has_payment_method(
        self, authenticated_client
    ):
        USERS_CHECK_PAYMENT_URL = '{}{}/'.format(USERS_BASE_ENDPOINT, 'payment_methods')
        response = authenticated_client.get(USERS_CHECK_PAYMENT_URL)

        assert response.status_code == 200
        assert response.data['has_payment_method'] is None


class TestUserPermission:
    def _has_permission(self, client: Client, username, should_have_access):
        response = client.get('{}{}/'.format(USERS_BASE_ENDPOINT, username))
        if should_have_access:
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_normal_users_can_not_see_list_of_users_and_can_retrieve_only_their_profile(
        self, authenticated_client, admin_client, user_and_password
    ):
        response = authenticated_client.get(USERS_BASE_ENDPOINT)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        self._has_permission(authenticated_client, user_and_password[0].username, True)
        self._has_permission(authenticated_client, 'admin', False)

    def test_admin_user_can_access_anything_in_users_endpoint(
        self, authenticated_client, admin_client, user_and_password
    ):
        response = admin_client.get(USERS_BASE_ENDPOINT)
        assert response.status_code == status.HTTP_200_OK
        # There'll be 3 users, 1 anonymous user created by default, 1 admin created by admin_client and
        # 1 normal user which we created by importing fixture authenticated_client
        assert response.data.__len__() == 3

        self._has_permission(admin_client, user_and_password[0].username, True)
        self._has_permission(admin_client, 'admin', True)

    def test_fetch_bookmarked_solutions_of_user(
        self, authenticated_client, user_and_password, example_solution
    ):
        SolutionBookmark.objects.create(
            solution=example_solution, user=user_and_password[0]
        )
        user_profile_url = '{}{}/'.format(
            USERS_BASE_ENDPOINT, user_and_password[0].username
        )
        response = authenticated_client.get(user_profile_url)

        assert response.status_code == 200
        assert (
            response.data['bookmarked_solutions'][0]['solution']['title']
            == example_solution.title
        )


class TestProviderBookingsList:
    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def _make_user_customer_with_default_payment_method(
        self,
        user,
        example_stripe_attach_payment_method_customer_object,
        example_stripe_customer_object,
    ):
        example_stripe_payment_method = StripePaymentMethod.objects.create(
            id=example_stripe_attach_payment_method_customer_object['id'],
            billing_details=example_stripe_attach_payment_method_customer_object[
                'billing_details'
            ],
        )
        example_stripe_customer = StripeCustomer.objects.create(
            id=example_stripe_customer_object['id'],
            email=user.email,
            default_payment_method=example_stripe_payment_method,
        )
        User.objects.filter(id=user.id).update(stripe_customer=example_stripe_customer)

    def test_authenticated_user_should_fetch_provider_solution_bookings_list(
        self, authenticated_client, user_and_password, admin_user, example_solution
    ):
        SolutionBooking.objects.create(
            solution=example_solution, booked_by=user_and_password[0]
        )

        response = authenticated_client.get(
            '{}{}/{}/'.format(
                USERS_BASE_ENDPOINT, admin_user.username, 'provider_bookings'
            )
        )

        assert response.status_code == 200
        assert response.data[0]['solution']['title'] == example_solution.title
        assert (
            response.data[0]['booked_by']['username'] == user_and_password[0].username
        )

    @override_settings(STRIPE_TEST_PUBLISHED_KEY='')
    def test_authenticated_user_should_tracked_time(
        self,
        user_and_password,
        authenticated_client,
        example_solution,
        example_solution_booking,
        example_stripe_usage_object,
        example_stripe_product_create_event,
        example_stripe_price_create_event,
        example_stripe_subscription_object,
        example_stripe_customer_object,
        example_stripe_attach_payment_method_customer_object_1,
        example_stripe_attach_payment_method_customer_object_2,
        example_stripe_customer_has_default_payment_method_object,
        mocker,
    ):
        # Subscribe the solution.
        test_user_payment = TestUserPayment()
        solution_booking_response = test_user_payment._customer_subscribe_payment(
            mocker,
            example_stripe_subscription_object,
            example_stripe_price_create_event,
            example_stripe_product_create_event,
            example_solution,
            user_and_password,
            example_stripe_attach_payment_method_customer_object_1,
            authenticated_client,
            example_stripe_customer_object,
        )

        # Create mocker for patching create usage record API.
        mocker.patch(
            'stripe.SubscriptionItem.create_usage_record',
            return_value=util.convert_to_stripe_object(example_stripe_usage_object),
        )

        example_product = StripeProduct.objects.get(
            id=example_stripe_product_create_event.data['object']['id']
        )
        example_solution.stripe_product = example_product
        example_solution.save()

        provider_time_track_url = '{}{}/'.format(
            USERS_BASE_ENDPOINT, 'tracking_time_report'
        )
        response = authenticated_client.post(
            provider_time_track_url,
            {
                'tracking_time': [
                    {
                        "date": "2022-01-28T23:59:59Z",
                        "tracked_hours": "2.0",
                    },
                    {
                        "date": "2022-01-29T23:59:59Z",
                        "tracked_hours": "1.0",
                    },
                ],
                'booking_id': solution_booking_response.data['solution_booking_id'],
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.data['tracking_times'][0]['tracked_hours'] == '2.0'
        assert response.data['tracking_times'][1]['tracked_hours'] == '1.0'
