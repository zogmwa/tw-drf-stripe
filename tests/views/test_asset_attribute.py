from rest_framework import status
import pytest

ASSET_ATTRIBUTES_ENDPOINT = 'http://127.0.0.1:8000/asset_attributes/'
ASSET_ATTRIBUTE_VOTES_ENDPOINT = 'http://127.0.0.1:8000/asset_attribute_votes/'


class TestAssetAttributeVotedByMe:
    def test_for_anonymous_user_voted_by_me_should_not_be_passed_in_response_of_list_or_for_a_single_asset(
        self,
        authenticated_client,
        unauthenticated_client,
        example_asset,
        example_asset_attribute,
    ):
        # Vote on asset attribute
        authenticated_client.post(
            ASSET_ATTRIBUTES_ENDPOINT,
            {'asset': example_asset.id, 'attribute': example_asset_attribute.id},
        )

        # Get attributes list
        response = unauthenticated_client.get(ASSET_ATTRIBUTES_ENDPOINT)
        assert response.status_code == 200
        assert 'voted_by_me' not in response.data[0].keys()

        # Get attribute detail
        asset_attribute_url = '{}{}/'.format(
            ASSET_ATTRIBUTES_ENDPOINT, example_asset_attribute.id
        )
        response = unauthenticated_client.get(asset_attribute_url)
        assert response.status_code == 200
        assert 'used_by_me' not in response.data.keys()

    @pytest.mark.parametrize(
        "voted",
        [True, False],
    )
    def test_for_logged_in_user_voted_by_me_field_should_be_returned_and_show_correct_value(
        self,
        authenticated_client,
        example_asset,
        example_asset_attribute,
        example_asset_attribute_vote,
        voted,
    ):
        if voted:
            authenticated_client.post(
                ASSET_ATTRIBUTES_ENDPOINT,
                {'asset': example_asset.id, 'attribute': example_asset_attribute.id},
            )
        else:
            authenticated_client.delete(
                '{}{}/'.format(
                    ASSET_ATTRIBUTE_VOTES_ENDPOINT, example_asset_attribute_vote.id
                )
            )

        # Get attributes list
        response = authenticated_client.get(ASSET_ATTRIBUTES_ENDPOINT)
        assert response.status_code == 200
        assert 'voted_by_me' in response.data[0].keys()
        assert response.data[0]['voted_by_me'] == voted

        # Get attribute detail
        asset_attribute_url = '{}{}/'.format(
            ASSET_ATTRIBUTES_ENDPOINT, example_asset_attribute.id
        )
        response = authenticated_client.get(asset_attribute_url)
        assert response.status_code == 200
        assert 'voted_by_me' in response.data.keys()
        assert response.data['voted_by_me'] == voted
