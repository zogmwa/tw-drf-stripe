from rest_framework import status

from api.models import Asset, Tag
import pytest
from django.test import Client

from api.models.asset_snapshot import AssetSnapshot

from api.views.asset import AssetViewSet
from tests.common import login_client


ASSETS_BASE_ENDPOINT = 'http://127.0.0.1:8000/assets/'


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


class TestViewEditPermissionOfAsset:
    def _validate_patch_put_delete_request(
        self, client: Client, asset_slug, should_pass: bool, mocker
    ):
        mocker.patch.object(
            AssetViewSet,
            '_get_assets_db_qs_via_elasticsearch_query',
            return_value=Asset.objects.all(),
        )
        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, asset_slug)

        if should_pass is False:
            response = client.patch(
                asset_url, {'name': 'new name'}, content_type='application/json'
            )
            assert response.status_code == 403

            response = client.put(
                asset_url, {'name': 'new name'}, content_type='application/json'
            )
            assert response.status_code == 403

            response = client.delete(asset_url)
            assert response.status_code == 403
        else:
            response = client.patch(
                asset_url, {'name': 'new name'}, content_type='application/json'
            )
            assert response.status_code == 200

            response = client.put(
                asset_url, {'name': 'new name'}, content_type='application/json'
            )
            assert response.status_code == 200

            response = client.delete(asset_url)
            assert response.status_code == 204

    def test_anonymous_user_should_be_able_to_access_list_of_assets_or_particular_asset(
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

        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = unauthenticated_client.get(asset_url)
        assert response.status_code == 200
        assert response.data['slug'] == example_asset.slug

    def test_user_can_not_make_patch_put_delete_request(
        self, authenticated_client, example_asset, mocker
    ):
        self._validate_patch_put_delete_request(
            authenticated_client, example_asset.slug, False, mocker
        )

    def test_owner_not_present_submitted_by_user_can_edit_asset(
        self, authenticated_client, mocker
    ):
        response = _create_asset(authenticated_client)
        self._validate_patch_put_delete_request(
            authenticated_client, response.data['slug'], True, mocker
        )

    def test_owner_is_present_submitted_by_user_can_not_edit_asset(
        self, authenticated_client, admin_user_and_password, mocker
    ):
        response = _create_asset(authenticated_client)
        Asset.objects.filter(slug=response.data['slug']).update(
            owner=admin_user_and_password[0]
        )
        self._validate_patch_put_delete_request(
            authenticated_client, response.data['slug'], False, mocker
        )

    def test_owner_can_edit_asset(
        self, authenticated_client, user_and_password, admin_client, mocker
    ):
        response = _create_asset(admin_client)
        Asset.objects.filter(slug=response.data['slug']).update(
            owner=user_and_password[0]
        )
        self._validate_patch_put_delete_request(
            authenticated_client, response.data['slug'], True, mocker
        )


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

        asset_query = '{}similar/?slug={}&include_self={}'.format(
            ASSETS_BASE_ENDPOINT, example_asset.slug, include_self
        )

        response = authenticated_client.get(asset_query)

        assert response.status_code == 200
        results = response.data['results']

        if int(include_self):
            assert len(results) == 2
        else:
            assert len(results) == 1
            assert results[0]['id'] == similar_asset.id

    @pytest.mark.parametrize('ordering', ['avg_rating', '-avg_rating'])
    def test_ascending_and_descending_sorting_by_avg_rating(
        self, authenticated_client, example_asset, ordering, mocker
    ):
        # Create 2 similar assets similar to example_asset
        similar_assets = []
        non_sorted_avg_rating_values = [7, 3]
        # The first asset i.e. example_asset should have an avg_rating of 0. So a non sorted order will be like 0, 7, 3
        for i in range(2):
            similar_asset = Asset.objects.create(
                name='Similar to Example Asset {}'.format(i + 1),
                slug='example-assset-similar-{}'.format(i + 1),
                short_description='test',
                description='test',
                avg_rating=non_sorted_avg_rating_values[i],
            )
            similar_asset.tags.set(example_asset.tags.all())
            similar_asset.save()
            similar_assets.append(similar_asset)

        mocker.patch.object(
            AssetViewSet,
            '_get_assets_db_qs_via_elasticsearch_query',
            return_value=Asset.objects.all(),
        )

        asset_query = '{}similar/?slug={}&include_self=1&ordering={}'.format(
            ASSETS_BASE_ENDPOINT,
            example_asset.slug,
            ordering,
        )

        response = authenticated_client.get(asset_query)

        assert response.status_code == 200
        results = response.data['results']
        rating_order = [asset['avg_rating'] for asset in results]

        # Don't worry about O(n log n) time-complexiting of sorting here because the list is small
        if ordering == '-avg_rating':
            # Descending
            assert rating_order[::-1] == sorted(rating_order)
        else:
            # Ascending
            assert rating_order == sorted(rating_order)

        assert len(results) == 3


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

    @pytest.mark.parametrize(
        "method, auth_client, is_owner, is_admin",
        [
            ('put', pytest.lazy_fixture("authenticated_client"), True, False),
            ('patch', pytest.lazy_fixture("authenticated_client"), True, False),
            ('put', pytest.lazy_fixture("authenticated_client"), False, False),
            ('patch', pytest.lazy_fixture("authenticated_client"), False, False),
            ('patch', pytest.lazy_fixture("admin_client"), False, True),
            ('put', pytest.lazy_fixture("admin_client"), False, True),
        ],
    )
    # @pytest.mark.parametrize('method', ['put', 'patch'])
    def test_update_existing_asset_with_new_snapshots(
        self, user_and_password, example_asset, method, auth_client, is_owner, is_admin
    ):
        if is_owner:
            Asset.objects.filter(slug=example_asset.slug).update(
                owner=user_and_password[0]
            )

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
            response = auth_client.put(
                put_endpoint, test_asset_data, content_type='application/json'
            )
        else:
            response = auth_client.patch(
                put_endpoint, test_asset_data, content_type='application/json'
            )
        if is_owner or is_admin:
            assert response.status_code == 200
            updated_asset = Asset.objects.get(id=example_asset.id)
            self._verify_updated_asset_and_its_associated_snapshot(
                example_asset, updated_asset, test_asset_data['snapshots'][0]['url']
            )
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "auth_client, is_owner, is_admin",
        [
            (pytest.lazy_fixture("authenticated_client"), True, False),
            (pytest.lazy_fixture("authenticated_client"), False, False),
            (pytest.lazy_fixture("admin_client"), False, True),
        ],
    )
    def test_update_existing_asset_with_existing_snapshots(
        self,
        example_asset,
        user_and_password,
        auth_client,
        is_owner,
        is_admin,
    ):

        if is_owner:
            Asset.objects.filter(slug=example_asset.slug).update(
                owner=user_and_password[0]
            )

        existing_asset_snapshot = AssetSnapshot.objects.create(
            url='https://miro.medium.com/max/591/1*8r_Ru1Rnju6p8renaAdp5Q.jpeg'
        )
        test_asset_data = {
            'slug': example_asset.slug,
            'snapshots': [{'url': existing_asset_snapshot.url}],
        }

        put_endpoint = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = auth_client.patch(
            put_endpoint, test_asset_data, content_type='application/json'
        )
        if is_owner or is_admin:
            assert response.status_code == 200
            updated_asset = Asset.objects.get(id=example_asset.id)
            self._verify_updated_asset_and_its_associated_snapshot(
                example_asset, updated_asset, test_asset_data['snapshots'][0]['url']
            )
        else:
            assert response.status_code is status.HTTP_403_FORBIDDEN


class TestAssetUsedByUser:
    def _check_if_user_asset_usage_record_exists_for_currrent_user_and_asset(
        self, asset, expected_count
    ):
        assert asset.users.count() == expected_count

    def _asset_used_endpoint(self, asset, used_by_me: str):
        url = '{}{}/{}/?used_by_me={}'.format(
            ASSETS_BASE_ENDPOINT, asset.slug, 'used_by_me', used_by_me
        )
        return url

    @pytest.mark.parametrize(
        "asset_used, expected_count",
        [('true', 1), ('false', 0)],
    )
    def test_if_user_marks_asset_as_used_then_there_should_be_one_row_presenting_this(
        self,
        user_and_password,
        authenticated_client,
        example_asset,
        asset_used,
        expected_count,
    ):
        response = authenticated_client.post(
            self._asset_used_endpoint(example_asset, asset_used),
        )
        if asset_used == 'true':
            assert response.status_code == status.HTTP_201_CREATED
        else:
            assert response.status_code == status.HTTP_204_NO_CONTENT
        self._check_if_user_asset_usage_record_exists_for_currrent_user_and_asset(
            example_asset, expected_count
        )

    def test_if_user_first_marks_asset_as_used_then_unmarks_it(
        self,
        user_and_password,
        authenticated_client,
        example_asset,
    ):
        response = authenticated_client.post(
            self._asset_used_endpoint(example_asset, 'true'),
        )
        assert response.status_code == status.HTTP_201_CREATED
        self._check_if_user_asset_usage_record_exists_for_currrent_user_and_asset(
            example_asset, 1
        )

        # None should not change anything
        response = authenticated_client.post(
            self._asset_used_endpoint(example_asset, '')
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self._check_if_user_asset_usage_record_exists_for_currrent_user_and_asset(
            example_asset, 1
        )

        response = authenticated_client.post(
            self._asset_used_endpoint(example_asset, 'false')
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        self._check_if_user_asset_usage_record_exists_for_currrent_user_and_asset(
            example_asset, 0
        )

    def test_for_anonymous_user_used_by_me_field_should_not_be_passed_in_response_of_list_or_for_a_single_asset(
        self, unauthenticated_client, mocker, example_asset, example_tag
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
        assert 'used_by_me' not in response.data['results'][0].keys()

        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = unauthenticated_client.get(asset_url)
        assert response.status_code == 200
        assert response.data['slug'] == example_asset.slug
        assert 'used_by_me' not in response.data.keys()

    @pytest.mark.parametrize(
        "is_asset_used",
        [True, False],
    )
    def test_for_logged_in_user_used_by_me_field_should_be_returned_and_show_correct_value(
        self, authenticated_client, example_asset, example_tag, mocker, is_asset_used
    ):
        if is_asset_used:
            authenticated_client.post(
                self._asset_used_endpoint(example_asset, 'true'),
            )

        mocker.patch.object(
            AssetViewSet,
            '_get_assets_db_qs_via_elasticsearch_query',
            return_value=Asset.objects.all(),
        )

        asset_list_url = '{}?q={}'.format(ASSETS_BASE_ENDPOINT, example_tag.name)
        response = authenticated_client.get(asset_list_url)
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['used_by_me'] == is_asset_used

        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = authenticated_client.get(asset_url)
        assert response.status_code == 200
        assert response.data['slug'] == example_asset.slug
        assert response.data['used_by_me'] == is_asset_used


class TestAssetVotedByMe:
    def test_for_anonymous_user_my_asset_vote_field_should_not_be_passed_in_response_of_list_or_for_a_single_asset(
        self, unauthenticated_client, mocker, example_asset, example_tag
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
        assert 'my_asset_vote' not in response.data['results'][0].keys()

        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = unauthenticated_client.get(asset_url)
        assert response.status_code == 200
        assert response.data['slug'] == example_asset.slug
        assert 'my_asset_vote' not in response.data.keys()

    @pytest.mark.parametrize(
        "is_asset_voted",
        [True, False],
    )
    def test_for_logged_in_user_my_asset_vote_field_should_be_returned_and_show_correct_value(
        self,
        authenticated_client,
        example_asset,
        example_tag,
        mocker,
        is_asset_voted,
        user_and_password,
    ):
        mocker.patch.object(
            AssetViewSet,
            '_get_assets_db_qs_via_elasticsearch_query',
            return_value=Asset.objects.all(),
        )

        if is_asset_voted:
            vote = example_asset.votes.create(user=user_and_password[0])

        asset_list_url = '{}?q={}'.format(ASSETS_BASE_ENDPOINT, example_tag.name)
        response = authenticated_client.get(asset_list_url)
        assert response.status_code == 200
        assert response.data['count'] == 1
        if is_asset_voted:
            assert response.data['results'][0]['my_asset_vote'] == vote.id
        else:
            assert response.data['results'][0]['my_asset_vote'] is None

        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = authenticated_client.get(asset_url)
        assert response.status_code == 200
        assert response.data['slug'] == example_asset.slug
        if is_asset_voted:
            assert response.data['my_asset_vote'] == vote.id
        else:
            assert response.data['my_asset_vote'] is None


class TestAssetIsOwned:
    def test_for_anonymous_user_is_owned_field_should_not_be_passed_in_response_of_list_or_for_a_single_asset(
        self, unauthenticated_client, mocker, example_asset, example_tag
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
        assert 'is_owned' not in response.data['results'][0].keys()

        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = unauthenticated_client.get(asset_url)
        assert response.status_code == 200
        assert response.data['slug'] == example_asset.slug
        assert 'is_owned' not in response.data.keys()

    @pytest.mark.parametrize(
        "is_owned",
        [False, True],
    )
    def test_for_logged_in_user_is_owned_field_should_be_returned_and_show_correct_value(
        self,
        authenticated_client,
        example_asset,
        example_tag,
        mocker,
        is_owned,
        user_and_password,
    ):
        mocker.patch.object(
            AssetViewSet,
            '_get_assets_db_qs_via_elasticsearch_query',
            return_value=Asset.objects.all(),
        )

        if is_owned:
            example_asset.owner = user_and_password[0]
            example_asset.save()

        asset_list_url = '{}?q={}'.format(ASSETS_BASE_ENDPOINT, example_tag.name)
        response = authenticated_client.get(asset_list_url)
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['is_owned'] == is_owned

        asset_url = '{}{}/'.format(ASSETS_BASE_ENDPOINT, example_asset.slug)
        response = authenticated_client.get(asset_url)
        assert response.status_code == 200
        assert response.data['slug'] == example_asset.slug
        assert response.data['is_owned'] == is_owned


class TestAssetCompare:
    def test_for_compare_less_than_2_or_more_than_3_should_return_bad_request_error(
        self,
        unauthenticated_client,
        example_asset,
        example_asset_2,
        example_asset_3,
        example_asset_4,
    ):
        response = unauthenticated_client.get(
            '{}compare/?asset__slugs={}'.format(
                ASSETS_BASE_ENDPOINT,
                example_asset.slug,
            )
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = unauthenticated_client.get(
            '{}compare/?asset__slugs={}&asset__slugs={}&asset__slugs={}&asset__slugs={}'.format(
                ASSETS_BASE_ENDPOINT,
                example_asset.slug,
                example_asset_2.slug,
                example_asset_3.slug,
                example_asset_4.slug,
            )
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_for_compare_with_non_existing_asset_should_return_not_found_error(
        self, unauthenticated_client, example_asset, example_asset_2
    ):
        response = unauthenticated_client.get(
            '{}compare/?asset__slugs={}&asset__slugs={}'.format(
                ASSETS_BASE_ENDPOINT, example_asset.slug, 'none-existing-asset-slug'
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_for_compare_with_2_or_3_assets_should_return_correct_values(
        self, unauthenticated_client, example_asset, example_asset_2, example_asset_3
    ):
        response = unauthenticated_client.get(
            '{}compare/?asset__slugs={}&asset__slugs={}'.format(
                ASSETS_BASE_ENDPOINT, example_asset.slug, example_asset_2.slug
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]['id'] == example_asset.id
        assert response.data[1]['id'] == example_asset_2.id

        response = unauthenticated_client.get(
            '{}compare/?asset__slugs={}&asset__slugs={}&asset__slugs={}'.format(
                ASSETS_BASE_ENDPOINT,
                example_asset.slug,
                example_asset_2.slug,
                example_asset_3.slug,
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]['id'] == example_asset.id
        assert response.data[1]['id'] == example_asset_2.id
        assert response.data[2]['id'] == example_asset_3.id
