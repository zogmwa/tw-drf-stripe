from api.models import Asset, Tag, AssetVote, LinkedTag
import pytest

from api.models.asset_snapshot import AssetSnapshot
from api.views.asset import AssetViewSet

ASSETS_BASE_ENDPOINT = 'http://127.0.0.1:8000/assets/'


def test_submitted_by_is_set_to_logged_in_user_when_saving_asset(
    user_and_password, authenticated_client
):
    # Create a mock request with the user object set (simulating a logged in user)
    asset_slug = 'test_slug'
    asset_name = 'test_asset'
    asset_description = 'Some test description'
    asset_short_description = 'short description of asset'
    response = authenticated_client.post(
        ASSETS_BASE_ENDPOINT,
        {
            'slug': asset_slug,
            'name': asset_name,
            'description': asset_description,
            'short_description': asset_short_description,
        },
    )
    assert response.status_code == 201

    asset = Asset.objects.get(slug=asset_slug)
    assert asset.submitted_by == user_and_password[0]


class AssetTagSearchCounter:
    """
    To test the tag search counter. We store how many times each tag is used to perform a search whenever the
    assets endpoint is hit.
    """

    def test_update_counter_of_tag_used_for_filtering_assets(
        self, authenticated_client
    ):
        def assert_counter(expected_count):
            assert Tag.objects.get(slug='tag-1').counter == expected_count
            assert Tag.objects.get(slug='tag-2').counter == expected_count

        asset_query = '{}?q=tag-1%20tag-2'.format(ASSETS_BASE_ENDPOINT)
        Tag.objects.create(
            slug='tag-1',
            name='tag 1',
        )
        Tag.objects.create(
            slug='tag-2',
            name='tag 2',
        )

        assert_counter(0)

        response = authenticated_client.get(asset_query)
        assert response.status_code == 200
        assert_counter(1)

    @pytest.mark.parametrize(
        "tag_slug, tag_name, query,",
        [('database', 'data', 'data'), ('data', 'data', 'database')],
    )
    def test_update_counter_of_tag_when_exactly_matched_with_searched_tag(
        self, authenticated_client, tag_slug, tag_name, query
    ):
        # When the user searches for assets by some tags, counter of those tags should only be incremented
        # which matches exactly with the searched tags. For example: if user searches 'database', then the counter
        # of a tag 'data' should not be incremented
        # Further, counter of those tags should also not increment whose name matches with the searched keyword
        asset_query = '{}?q={}'.format(ASSETS_BASE_ENDPOINT, query)
        Tag.objects.create(
            slug=tag_slug,
            name=tag_name,
        )
        assert Tag.objects.get(slug=tag_slug).counter == 0

        response = authenticated_client.get(asset_query)
        assert response.status_code == 200

        assert Tag.objects.get(slug=tag_slug).counter == 0


class TestAssetViewSetSimilarServices:
    @pytest.mark.parametrize(
        "include_self",
        ['0', '1'],
    )
    def test_similar_services(
        self, authenticated_client, example_asset, include_self, mocker
    ):
        similar_asset = Asset.objects.create(
            name='Simiar to Example Asset',
            slug='example-assset-similar',
            short_description='test',
            description='test',
        )
        similar_asset.tags.set(example_asset.tags.all())
        similar_asset.save()

        mocker.patch.object(
            AssetViewSet,
            '_get_assets_db_qs_via_elasticsearch_query',
            return_value=Asset.objects.all(),
        )

        asset_query = '{}similar/?name={}&include_self={}'.format(
            ASSETS_BASE_ENDPOINT, example_asset.name, include_self
        )

        response = authenticated_client.get(asset_query)

        assert response.status_code == 200
        results = response.data['results']

        if int(include_self):
            assert len(results) == 2
        else:
            assert len(results) == 1
            assert results[0]['id'] == similar_asset.id


class TestAssetCreate:
    def test_create_with_nested_field_snapshots(
        self, authenticated_client, example_asset, mocker
    ):
        test_asset_data = {
            'slug': 'google-cloud-gpu',
            'name': 'Google Cloud GPU',
            'website': 'https://cloud.google.com/gpu',
            'short_description': 'bla bla',
            'description': 'bla bla bla',
            'promo_video': 'https://www.youtube.com/embed/l3_uE4gdAWc',
            'snapshots': [
                {'url': 'https://miro.medium.com/max/591/1*8r_Ru1Rnju6p8renaAdp5Q.jpeg'}
            ],
        }

        response = authenticated_client.post(
            ASSETS_BASE_ENDPOINT, test_asset_data, content_type='application/json'
        )
        assert response.status_code == 201
        asset_gcp_gpu = Asset.objects.get(slug='google-cloud-gpu')

        # Check that the related snapshot object is created and that it's associated with the asset
        # crated in the POST request to the asset endpoint
        gcp_gpu_snapshot = AssetSnapshot.objects.get(asset=asset_gcp_gpu)
        assert gcp_gpu_snapshot.asset == asset_gcp_gpu
