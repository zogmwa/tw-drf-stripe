from rest_framework import status
import pytest
from api.models import LinkedAttribute


ASSET_ATTRIBUTES_ENDPOINT = 'http://127.0.0.1:8000/asset_attributes/'
ASSET_ATTRIBUTE_VOTES_ENDPOINT = 'http://127.0.0.1:8000/asset_attribute_votes/'


class TestAssetAttributeVotedByMe:
    def test_for_anonymous_user_my_asset_attribute_vote_should_not_be_passed_in_response_of_list_or_for_a_single_asset(
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
        assert 'my_asset_attribute_vote' not in response.data[0].keys()

        # Get attribute detail
        asset_attribute_url = '{}{}/'.format(
            ASSET_ATTRIBUTES_ENDPOINT, example_asset_attribute.id
        )
        response = unauthenticated_client.get(asset_attribute_url)
        assert response.status_code == 200
        assert 'my_asset_attribute_vote' not in response.data.keys()

    @pytest.mark.parametrize(
        "is_asset_attribute_voted",
        [True, False],
    )
    def test_for_logged_in_user_my_asset_attribute_vote_field_should_be_returned_and_show_correct_value(
        self,
        authenticated_client,
        example_asset,
        example_asset_attribute,
        example_asset_attribute_vote,
        is_asset_attribute_voted,
    ):
        if is_asset_attribute_voted:
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
        response = authenticated_client.get(
            '{}?asset__slug={}'.format(ASSET_ATTRIBUTES_ENDPOINT, example_asset.slug)
        )
        assert response.status_code == 200
        assert 'my_asset_attribute_vote' in response.data[0].keys()
        if is_asset_attribute_voted:
            assert (
                response.data[0]['my_asset_attribute_vote']
                == example_asset_attribute_vote.id
            )
        else:
            assert response.data[0]['my_asset_attribute_vote'] is None

        # Get attribute detail
        asset_attribute_url = '{}{}/?asset__slug={}'.format(
            ASSET_ATTRIBUTES_ENDPOINT, example_asset_attribute.id, example_asset.slug
        )
        response = authenticated_client.get(asset_attribute_url)
        assert response.status_code == 200
        assert 'my_asset_attribute_vote' in response.data.keys()
        if is_asset_attribute_voted:
            assert (
                response.data['my_asset_attribute_vote']
                == example_asset_attribute_vote.id
            )
        else:
            assert response.data['my_asset_attribute_vote'] is None


class TestAssetAttributeLinkedWithAsset:
    def test_for_logged_in_user_should_be_able_to_create_attribute_linked_with_asset(
        self,
        authenticated_client,
        example_asset,
    ):
        response = authenticated_client.post(
            ASSET_ATTRIBUTES_ENDPOINT,
            {'name': 'Test Asset Attribute', 'asset': example_asset.id},
            content_type='application/json',
        )

        assert response.status_code == 201

        linked_attribute = LinkedAttribute.objects.filter(
            asset__id=example_asset.id, attribute__id=response.data['id']
        )

        assert linked_attribute is not None
