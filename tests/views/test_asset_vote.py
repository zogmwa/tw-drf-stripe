import pytest
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from api.models import AssetVote

ASSET_VOTES_ENDPOINT = 'http://127.0.0.1:8000/asset_votes/'


class TestAssetVote:
    def test_create_with_logged_in_user(
        self,
        authenticated_client,
        user_and_password,
        example_asset,
    ):
        # Vote on asset attribute
        response = authenticated_client.post(
            ASSET_VOTES_ENDPOINT,
            {
                'asset': example_asset.id,
            },
        )
        assert response.status_code == HTTP_200_OK
        asset_vote = AssetVote.objects.get()
        assert asset_vote.user.id == user_and_password[0].id

    def test_get_and_delete(
        self,
        authenticated_client,
        user_and_password,
        example_asset,
    ):
        asset_vote_to_be_deleted = AssetVote.objects.create(
            asset=example_asset, user=user_and_password[0]
        )

        asset_vote_detail_endpoint = "{}{}/".format(
            ASSET_VOTES_ENDPOINT, asset_vote_to_be_deleted.id
        )
        get_asset_votes_response = authenticated_client.get(asset_vote_detail_endpoint)
        assert get_asset_votes_response.status_code == HTTP_200_OK
        assert get_asset_votes_response.data['id'] == asset_vote_to_be_deleted.id

        # Vote on asset attribute
        response = authenticated_client.delete(
            asset_vote_detail_endpoint,
            {
                'asset': example_asset.id,
            },
            content_type='application/json',
        )
        assert response.status_code == HTTP_204_NO_CONTENT
