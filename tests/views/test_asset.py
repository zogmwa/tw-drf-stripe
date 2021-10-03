from api.models import Asset, Tag, AssetVote, LinkedTag
import pytest
from django.test import Client

from api.models.asset_snapshot import AssetSnapshot
from api.models.user import User
from api.models.user_asset_usage import UserAssetUsage
from api.views.asset import AssetViewSet
from tests.common import login_client

ASSETS_BASE_ENDPOINT = 'http://127.0.0.1:8000/assets/'


# @pytest.fixture
def patch_elasticsearch(mocker):
    mocker.patch.object(
        AssetViewSet,
        '_get_assets_db_qs_via_elasticsearch_query',
        return_value=Asset.objects.all(),
    )


def _create_asset(client: Client):
    asset_slug = 'test_slug'
    asset_name = 'test_asset'
    asset_description = 'Some test description'
    asset_short_description = 'short description of asset'
    return client.post(
        ASSETS_BASE_ENDPOINT,
        {
            'slug': asset_slug,
            'name': asset_name,
            'description': asset_description,
            'short_description': asset_short_description,
        },
    )


def test_submitted_by_is_set_to_logged_in_user_when_saving_asset(
    user_and_password, authenticated_client
):
    # Create a mock request with the user object set (simulating a logged in user)
    asset_slug = 'test_slug'
    response = _create_asset(authenticated_client)
    assert response.status_code == 201

    asset = Asset.objects.get(slug=asset_slug)
    assert asset.submitted_by == user_and_password[0]


class TestUnpublishedAsset:
    def _link_tag(self, example_tag, asset):
        asset.tags.add(example_tag)
        asset.save()
        return asset

    def _validate_access_to_unpublished_asset(
        self, client: Client, should_have_access: bool, example_tag, asset, mocker
    ):
        if should_have_access:
            expected_count = 1
            status_code = 200
        else:
            expected_count = 0
            status_code = 404

        mocker.patch.object(
            AssetViewSet,
            '_get_assets_db_qs_via_elasticsearch_query',
            return_value=Asset.objects.all(),
        )

        asset_retrive_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, asset.slug)
        response = client.get(asset_retrive_url)
        assert response.status_code == status_code

    def test_unpublished_asset_should_be_visible_to_user_who_submitted_it_in_list_and_retrieve(
        self, authenticated_client, example_tag, mocker
    ):
        response = _create_asset(authenticated_client)
        asset = self._link_tag(example_tag, Asset.objects.get(id=response.data['id']))
        assert asset.is_published is False

        self._validate_access_to_unpublished_asset(
            authenticated_client, True, example_tag, asset, mocker
        )

    def test_other_users_can_not_see_unpublished_assets(
        self, admin_client, example_tag, mocker, authenticated_client
    ):
        response = _create_asset(admin_client)
        asset = self._link_tag(example_tag, Asset.objects.get(id=response.data['id']))
        assert asset.is_published is False

        self._validate_access_to_unpublished_asset(
            authenticated_client, False, example_tag, asset, mocker
        )

    def test_admin_staff_can_see_unpublished_assets(
        self,
        authenticated_client,
        admin_user_and_password,
        staff_user_and_password,
        example_tag,
        mocker,
    ):
        response = _create_asset(authenticated_client)
        asset = self._link_tag(example_tag, Asset.objects.get(id=response.data['id']))
        assert asset.is_published is False

        users_and_password = [admin_user_and_password, staff_user_and_password]
        for user_and_password in users_and_password:
            self._validate_access_to_unpublished_asset(
                login_client(user_and_password),
                True,
                example_tag,
                asset,
                mocker,
            )

    def test_anonymous_user_should_be_able_to_access_list_of_assets(
        self, unauthenticated_client, example_tag, mocker, example_asset
    ):
        mocker.patch.object(
            AssetViewSet,
            '_get_assets_db_qs_via_elasticsearch_query',
            return_value=Asset.objects.all(),
        )

        asset_list_url = '{}?q={}'.format(ASSETS_BASE_ENDPOINT, example_tag.name)
        response = unauthenticated_client.get(asset_list_url)
        assert response.status_code == 200
        assert response.data['count'] == 1


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


class TestAssetCreateUpdateWithOneManyFieldSnapshots:
    def test_create_asset_with_new_snapshots(
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

    def _verify_updated_asset_and_its_associated_snapshot(
        self, example_asset, updated_asset, expected_snapshot_url
    ):
        assert updated_asset == example_asset
        updated_asset_snapshot = updated_asset.snapshots.get()
        assert updated_asset_snapshot.asset.id == example_asset.id
        assert updated_asset_snapshot.url == expected_snapshot_url

    @pytest.mark.parametrize('method', ['put', 'patch'])
    def test_update_existing_asset_with_new_snapshots(
        self, authenticated_client, example_asset, method
    ):
        test_asset_data = {
            'slug': example_asset.slug,
            'name': example_asset.name,
            'snapshots': [
                {'url': 'https://miro.medium.com/max/591/1*8r_Ru1Rnju6p8renaAdp5Q.jpeg'}
            ],
        }

        put_endpoint = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)

        # If all required fields e.g. 'name' are also passed in the data then 'put' can also be used instead of 'patch`
        # For patch, only the pk/lookup field needs to be passed and the fields being updated
        if method == 'put':
            response = authenticated_client.put(
                put_endpoint, test_asset_data, content_type='application/json'
            )
        else:
            response = authenticated_client.patch(
                put_endpoint, test_asset_data, content_type='application/json'
            )

        assert response.status_code == 200
        updated_asset = Asset.objects.get(id=example_asset.id)
        self._verify_updated_asset_and_its_associated_snapshot(
            example_asset, updated_asset, test_asset_data['snapshots'][0]['url']
        )

    def test_update_existing_asset_with_existing_snapshots(
        self,
        authenticated_client,
        example_asset,
    ):

        existing_asset_snapshot = AssetSnapshot.objects.create(
            url='https://miro.medium.com/max/591/1*8r_Ru1Rnju6p8renaAdp5Q.jpeg'
        )
        test_asset_data = {
            'slug': example_asset.slug,
            'snapshots': [{'url': existing_asset_snapshot.url}],
        }

        put_endpoint = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = authenticated_client.patch(
            put_endpoint, test_asset_data, content_type='application/json'
        )
        assert response.status_code == 200
        updated_asset = Asset.objects.get(id=example_asset.id)
        self._verify_updated_asset_and_its_associated_snapshot(
            example_asset, updated_asset, test_asset_data['snapshots'][0]['url']
        )


class TestAssetUsedByUser:
    def _check_if_useer_asset_usage_record_exists_for_currrent_user_and_asset(
        self, asset, expected_count
    ):
        assert asset.users.count() == expected_count

    @pytest.mark.parametrize(
        "asset_used, expected_count",
        [('true', 1), ('false', 0)],
    )
    def test_if_user_marks_asset_as_used_then_there_should_be_one_row_present_this(
        self,
        user_and_password,
        authenticated_client,
        example_asset,
        asset_used,
        expected_count,
    ):
        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = authenticated_client.patch(
            asset_url, {'used_by_me': asset_used}, 'application/json'
        )
        assert response.status_code == 200
        self._check_if_useer_asset_usage_record_exists_for_currrent_user_and_asset(
            example_asset, expected_count
        )

    def test_if_user_first_marks_asset_as_used_then_unmarks_it(
        self,
        user_and_password,
        authenticated_client,
        example_asset,
    ):
        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = authenticated_client.patch(
            asset_url, {'used_by_me': 'true'}, 'application/json'
        )
        assert response.status_code == 200
        self._check_if_useer_asset_usage_record_exists_for_currrent_user_and_asset(
            example_asset, 1
        )

        # None should not change anything
        response = authenticated_client.patch(asset_url, {}, 'application/json')
        assert response.status_code == 200
        self._check_if_useer_asset_usage_record_exists_for_currrent_user_and_asset(
            example_asset, 1
        )

        response = authenticated_client.patch(
            asset_url, {'used_by_me': 'false'}, 'application/json'
        )
        assert response.status_code == 200
        self._check_if_useer_asset_usage_record_exists_for_currrent_user_and_asset(
            example_asset, 0
        )
