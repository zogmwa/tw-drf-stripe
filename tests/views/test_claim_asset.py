import pytest
from api.models.user import User
from api.views.claim_asset import ClaimAssetViewSet
from tests.common import login_client
from django.test import Client


CLAIM_ASSET_BASE_ENDPOINT = 'http://127.0.0.1:8000/claim_asset/'


def _authenticated_client(user_and_password):
    client = Client()
    client.login(username=user_and_password[0].username, password=user_and_password[1])
    assert client.session['_auth_user_id'] == str(user_and_password[0].id)
    return client


@pytest.fixture
def _create_claim_asset_request_by_staff(staff_user_and_password, example_asset):
    client = login_client(staff_user_and_password)
    response = client.post(
        CLAIM_ASSET_BASE_ENDPOINT,
        {
            'asset': example_asset.id,
            'comment': 'claim request by staff',
        },
    )
    assert response.status_code == 201
    return response


def _create_asset_claim_request(client, user_ans_password, asset):
    response = client.post(
        CLAIM_ASSET_BASE_ENDPOINT,
        {
            'asset': asset.id,
            'comment': 'claim request by' + user_ans_password[0].username,
        },
    )
    assert response.status_code == 201
    return response


class TestClaimAssetListAndRetrieve:
    def test_anonymous_user_can_not_view_list_retrieve(self, unauthenticated_client):
        response = unauthenticated_client.get(CLAIM_ASSET_BASE_ENDPOINT)
        assert response.status_code == 401

    def test_anonymous_user_can_not_retrieve_any_asset_claim_object(
        self, unauthenticated_client, _create_claim_asset_request_by_staff
    ):
        claim_asset_object_url = '{}{}/'.format(
            CLAIM_ASSET_BASE_ENDPOINT, _create_claim_asset_request_by_staff.data['id']
        )
        response = unauthenticated_client.get(claim_asset_object_url)
        assert response.status_code == 401

    def test_user_can_only_view_list_containing_users_asset_claim_requests(
        self,
        user_and_password,
        authenticated_client,
        _create_claim_asset_request_by_staff,
        example_asset,
    ):
        _create_asset_claim_request(
            authenticated_client, user_and_password, example_asset
        )

        response = authenticated_client.get(CLAIM_ASSET_BASE_ENDPOINT)
        assert response.status_code == 200
        assert response.data.__len__() == 1
        assert response.data[0]['user']['username'] == user_and_password[0].username

    def test_user_can_not_change_status_of_asset_claim_request(
        self, authenticated_client, user_and_password, example_asset
    ):
        response = _create_asset_claim_request(
            authenticated_client, user_and_password, example_asset
        )

        claim_asset_object_url = '{}{}/'.format(
            CLAIM_ASSET_BASE_ENDPOINT, response.data['id']
        )

        assert response.data['status'] == 'Pending'
        response = authenticated_client.patch(
            claim_asset_object_url,
            {
                'status': 'Accepted',
            },
            content_type='application/json',
        )
        assert response.data['status'] == 'Pending'

    def test_user_can_retrieve_and_edit_objects_which_are_created_by_user(
        self,
        authenticated_client,
        user_and_password,
        _create_claim_asset_request_by_staff,
        example_asset,
    ):
        response = _create_asset_claim_request(
            authenticated_client, user_and_password, example_asset
        )

        claim_asset_object_url = '{}{}/'.format(
            CLAIM_ASSET_BASE_ENDPOINT, response.data['id']
        )

        response = authenticated_client.get(claim_asset_object_url)
        assert response.status_code == 200

        updated_comment = 'updated comment'
        response = authenticated_client.patch(
            claim_asset_object_url,
            {
                'comment': updated_comment,
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.data['comment'] == updated_comment

        claim_asset_object_url = '{}{}/'.format(
            CLAIM_ASSET_BASE_ENDPOINT, _create_claim_asset_request_by_staff.data['id']
        )
        response = authenticated_client.get(claim_asset_object_url)
        assert response.status_code == 403

    def test_admin_user_can_view_list_which_contains_all_asset_claim_requests(
        self,
        user_and_password,
        admin_client,
        _create_claim_asset_request_by_staff,
        example_asset,
    ):
        response = admin_client.post(
            CLAIM_ASSET_BASE_ENDPOINT,
            {
                'asset': example_asset.id,
                'comment': 'claim request by admin user',
            },
        )
        assert response.status_code == 201

        response = admin_client.get(CLAIM_ASSET_BASE_ENDPOINT)
        assert response.status_code == 200
        assert response.data.__len__() == 2

    def test_admin_can_retrieve_and_edit_any_claim_request_object_and_can_change_status_of_asset_claim_request(
        self, admin_client, _create_claim_asset_request_by_staff
    ):
        claim_asset_object_url = '{}{}/'.format(
            CLAIM_ASSET_BASE_ENDPOINT, _create_claim_asset_request_by_staff.data['id']
        )
        response = admin_client.get(claim_asset_object_url)
        assert response.status_code == 200

        updated_comment = 'comment updated by admin'
        updated_status = 'Accepted'
        response = admin_client.patch(
            claim_asset_object_url,
            {
                'comment': updated_comment,
                'status': updated_status,
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.data['comment'] == updated_comment
        assert response.data['status'] == updated_status
