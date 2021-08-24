from api.models import Asset, Tag, AssetVote, LinkedTag
import pytest

from api.views.asset import AssetViewSet


def test_submitted_by_is_set_to_logged_in_user_when_saving_asset(
    user_and_password, authenticated_client
):
    # Create a mock request with the user object set (simulating a logged in user)
    asset_url = 'http://127.0.0.1:8000/assets/'
    asset_slug = 'test_slug'
    asset_name = 'test_asset'
    asset_description = 'Some test description'
    asset_short_description = 'short description of asset'
    response = authenticated_client.post(
        asset_url,
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


def test_update_counter_of_tag_used_for_filtering_assets(authenticated_client):
    def assert_counter(expected_count):
        assert Tag.objects.get(slug='tag-1').counter == expected_count
        assert Tag.objects.get(slug='tag-2').counter == expected_count

    asset_query = 'http://127.0.0.1:8000/assets/?q=tag-1%20tag-2'
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
    "tag, tag_name, query,",
    [('database', 'data', 'data'), ('data', 'data', 'database')],
)
def test_update_counter_of_tag_when_exactly_matched_with_searched_tag(
    authenticated_client, tag, tag_name, query
):
    # When the user searches for assets by some tags, counter of those tags should only be incremented
    # which matches exactly with the searched tags. For example: if user searches 'database', then the counter
    # of a tag 'data' should not be incremented
    # Further, counter of those tags should also not increment whose name matches with the searched keyword
    asset_query = 'http://127.0.0.1:8000/assets/?q=' + query
    Tag.objects.create(
        slug=tag,
        name=tag_name,
    )
    assert Tag.objects.get(slug=tag).counter == 0

    response = authenticated_client.get(asset_query)
    assert response.status_code == 200

    assert Tag.objects.get(slug=tag).counter == 0


def test_list_should_be_sorted_by_upvotes_count_if_asked(
    user_and_password,
    authenticated_client,
    example_asset,
    example_tag,
    mocker,
):
    """
    This test will create 2 assets and first give one upvote to the first asset and check that
    the asset which was upvoted should come first in the returned list of assets by endpoint.
    Similarly, we will give one upvote to another asset and delete the previous upvote and check
    that the asset which got upvoted this time should come first
    Note: result will be sorted wrt upvote_counts only if there is a request which contains ?ordering=upvotes
    """

    def _check_upvote_counts_on_assets_is_a_non_increasing_sequence():
        upvotes_count = float('inf')
        for asset in response.data['results']:
            assert asset['upvotes_count'] <= upvotes_count
            upvotes_count = asset['upvotes_count']

    asset2 = Asset.objects.create(
        slug='asset2',
        name='asset2',
        website='https://mailchimp.com/',
        short_description='bla bla',
        description='bla bla bla',
        promo_video='https://www.youtube.com/embed/Q0hi9d1W3Ag',
    )

    asset2.tags.set([example_tag.id])
    asset2.save()
    example_asset.tags.set([example_tag.id])
    example_asset.save()

    assets_get_url = (
        'http://127.0.0.1:8000/assets/?ordering=upvotes&q=' + example_tag.slug
    )

    AssetVote.objects.create(
        is_upvote=True, asset_id=example_asset.id, user_id=user_and_password[0].id
    )

    mocker.patch.object(
        AssetViewSet,
        attribute='_get_assets_db_qs_from_es_query',
        return_value=Asset.objects.all(),
    )

    response = authenticated_client.get(assets_get_url)
    assert response.status_code == 200
    assert response.data['count'] == 2
    _check_upvote_counts_on_assets_is_a_non_increasing_sequence()

    AssetVote.objects.all().delete()
    assert AssetVote.objects.count() == 0
    AssetVote.objects.create(
        is_upvote=True, asset_id=asset2.id, user_id=user_and_password[0].id
    )

    response = authenticated_client.get(assets_get_url)
    assert response.status_code == 200
    assert response.data['count'] == 2
    _check_upvote_counts_on_assets_is_a_non_increasing_sequence()
