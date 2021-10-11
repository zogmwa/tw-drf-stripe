from rest_framework import status

from api.models import User, Organization, Asset
from tests.views.test_asset import _create_asset
import pytest
from django.test import Client


USERS_BASE_ENDPOINT = 'http://127.0.0.1:8000/users/'


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
