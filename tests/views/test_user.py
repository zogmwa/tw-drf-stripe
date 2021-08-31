from api.models import User, Organization
import pytest

USER_BASE_ENDPOINT = 'http://127.0.0.1:8000/users/'


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

    def test_when_user_update_by_creating_new_organization(
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

    def test_when_user_update_by_choosing_organization(
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

    def test_when_user_is_created_by_choosing_organization(
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
