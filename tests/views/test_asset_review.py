import pytest
from django.test import Client
from api.models import AssetReview, User

ASSET_REVIEW_URL = 'http://127.0.0.1:8000/asset_reviews/'


def test_review_user_is_set_to_logged_in_user_when_adding_a_new_review(
    user_and_password, authenticated_client, example_asset
):
    response = authenticated_client.post(
        ASSET_REVIEW_URL,
        {
            'asset': example_asset.id,
            'content': 'Test review',
            'rating': 9,
        },
    )
    assert response.status_code == 201

    review = AssetReview.objects.get(asset=example_asset)
    assert review.user == user_and_password[0]


class TestAssetReviewPermission:
    def test_asset_review_list_is_visible_to_users_without_login(
        self, unauthenticated_client
    ):
        response = unauthenticated_client.get(ASSET_REVIEW_URL)
        assert response.status_code == 200

    def test_requested_asset_review_is_visible_to_users_without_login(
        self, authenticated_client, unauthenticated_client, create_sample_asset_review
    ):
        response = create_sample_asset_review

        asset_review_id = response.data['id']
        asset_review_url = '{}{}/'.format(ASSET_REVIEW_URL, asset_review_id)

        unauthenticated_client_response = unauthenticated_client.get(asset_review_url)

        assert unauthenticated_client_response.status_code == 200

    def test_modify_operation_on_asset_review_for_a_logged_in_user(
        self, authenticated_client, create_sample_asset_review
    ):
        """
        Test Case: user logged in... create review... modify that review
        """
        create_asset_review_response = create_sample_asset_review

        asset_id = create_asset_review_response.data['asset']
        asset_review_id = create_asset_review_response.data['id']
        asset_review_url = '{}{}/'.format(ASSET_REVIEW_URL, asset_review_id)

        updated_review_content = 'Modified Test Asset Review'
        updated_review_rating = 8
        modify_asset_review_response = authenticated_client.put(
            asset_review_url,
            {
                'asset': asset_id,
                'content': updated_review_content,
                'rating': updated_review_rating,
            },
            content_type='application/json',
        )

        assert modify_asset_review_response.status_code == 200

        get_asset_review_response = authenticated_client.get(asset_review_url)

        assert get_asset_review_response.status_code == 200
        assert get_asset_review_response.data['content'] == updated_review_content
        assert get_asset_review_response.data['rating'] == updated_review_rating

    def test_modify_operation_on_asset_review_for_a_foreign_logged_in_user(
        self, create_sample_asset_review, foreign_authenticated_client
    ):
        """
        Test Case: logged in user... cannot modify a review of other user
        """
        create_asset_response = create_sample_asset_review

        asset_id = create_asset_response.data['asset']
        asset_review_id = create_asset_response.data['id']
        asset_review_url = '{}{}/'.format(ASSET_REVIEW_URL, asset_review_id)

        updated_review_content = 'Modified Test Asset Review'
        updated_review_rating = 8
        modify_asset_review_response = foreign_authenticated_client.put(
            asset_review_url,
            {
                'asset': asset_id,
                'content': updated_review_content,
                'rating': updated_review_rating,
            },
            content_type='application/json',
        )

        assert modify_asset_review_response.status_code == 403
        assert modify_asset_review_response.status_text == 'Forbidden'


@pytest.fixture
def create_sample_asset_review(authenticated_client, example_asset):
    return authenticated_client.post(
        ASSET_REVIEW_URL,
        {
            'asset': example_asset.id,
            'content': 'Test Asset Review',
            'rating': 9,
        },
    )


@pytest.fixture
def foreign_user_and_password():
    username = 'foreign-username'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user, password


@pytest.fixture()
def foreign_authenticated_client(foreign_user_and_password):
    client = Client()
    client.login(
        username=foreign_user_and_password[0].username,
        password=foreign_user_and_password[1],
    )
    assert client.session['_auth_user_id'] == str(foreign_user_and_password[0].id)
    return client
