import pytest
from django.db import IntegrityError

from api.models import AssetReview, User, Asset


def test_asset_review(example_asset, user_and_password):
    test_user = user_and_password[0]
    AssetReview.objects.create(
        asset=example_asset,
        user=test_user,
        rating=10,
    )

    # Creating a second review from the same user for the same asset should result in a unique constraint violation
    with pytest.raises(IntegrityError) as e:
        AssetReview.objects.create(
            asset=example_asset,
            user=test_user,
            rating=9,
        )
    assert 'unique constraint' in e.value.args[0]


def test_avg_rating_of_asset_should_be_correctly_updated_when_a_review_is_submitted_or_deleted(
    example_asset, user_and_password
):
    def assert_avg(expected_avg, expected_count):
        asset = Asset.objects.get(slug=example_asset.slug)

        assert AssetReview.objects.count() == expected_count
        assert asset.reviews_count == expected_count
        assert asset.avg_rating == expected_avg

    assert_avg(0, 0)

    test_user = user_and_password[0]
    AssetReview.objects.create(
        asset=example_asset,
        user=test_user,
        rating=8,
    )

    assert_avg(8, 1)

    username = 'username1'
    password = 'password'
    test_user2 = User.objects.create(username=username)
    test_user2.set_password(password)
    test_user2.save()

    AssetReview.objects.create(
        asset=example_asset,
        user=test_user2,
        rating=9,
    )

    assert_avg(8.5, 2)

    AssetReview.objects.filter(rating=9).delete()
    assert_avg(8, 1)
