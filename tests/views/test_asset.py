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
