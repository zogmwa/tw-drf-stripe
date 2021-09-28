from api.models import User, Organization
from tests.views.test_asset import _create_asset
import pytest

USER_BASE_ENDPOINT = 'http://127.0.0.1:8000/users/'


class TestSubmittedAssetsIsVisibleInProfilePage:
    def test_when_user_hits_profile_page_submitted_assets_should_be_visible_whether_published_or_not(
        self, authenticated_client, user_and_password
    ):
        asset_create_response = _create_asset(authenticated_client)
        assert asset_create_response.status_code == 201

        user_profile_url = '{}{}/'.format(
            USER_BASE_ENDPOINT, user_and_password[0].username
        )
        response = authenticated_client.get(user_profile_url)
        assert response.status_code == 200
        assert len(response.data['submitted_assets']) == 1
        assert (
            response.data['submitted_assets'][0]['id']
            == asset_create_response.data['id']
        )


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
            USER_BASE_ENDPOINT,
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
            USER_BASE_ENDPOINT, user_and_password[0].username
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
            USER_BASE_ENDPOINT, user_and_password[0].username
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
            USER_BASE_ENDPOINT,
            {'username': username, 'organization': {'name': organization_name}},
            'application/json',
        )

        assert response.status_code == 201
        self._test_organization_user_link(
            username, Organization.objects.get(name=organization_name).id
        )
