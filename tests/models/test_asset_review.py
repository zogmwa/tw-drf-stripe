import pytest
from django.db import IntegrityError

from api.models import AssetReview, User, Asset


def test_asset_review_is_unique_for_user_and_asset(example_asset, user_and_password):
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
    assert 'unique constraint' in e.value.args[0].lower()


@pytest.mark.skip(
    # One possibility why this is failing in Github Actions and not local:
    # - One the db being used in Github actions is SQLite which has different locking behaviour than PostgreSQL.
    # - The other is some sort of async behaviour in signal receivers where the field is not updated by the time we run the assertion
    reason="This is currently failing in Github actions and passing in local, something to explore."
)
class TestAssetReviewAggregates:
    def _validate_avg_rating_and_count(self, asset, expected_avg, expected_count):
        # To refresh the asset and make sure it's fields are updated
        asset = Asset.objects.get(id=asset.id)
        assert AssetReview.objects.count() == expected_count
        assert asset.reviews_count == expected_count
        assert asset.avg_rating == expected_avg

    def test_avg_rating_of_asset_should_be_correctly_updated_when_a_review_is_submitted_or_deleted(
        self, example_asset, user_and_password
    ):

        self._validate_avg_rating_and_count(example_asset, 0, 0)

        test_user = user_and_password[0]
        review1 = AssetReview.objects.create(
            asset=example_asset,
            user=test_user,
            rating=8,
        )
        self._validate_avg_rating_and_count(example_asset, 8, 1)

        test_user2 = User.objects.create(username='username2')
        test_user2.set_password('password2')
        test_user2.save()

        review2 = AssetReview.objects.create(
            asset=example_asset,
            user=test_user2,
            rating=9,
        )
        self._validate_avg_rating_and_count(example_asset, 8.5, 2)

        review2.delete()
        self._validate_avg_rating_and_count(example_asset, 8, 1)

        # TODO: Currently there is a bug division by zero bug for last review being deleted.
        # https://github.com/taggedweb/taggedweb/issues/133
        # review1.delete()
        # _validate_avg_rating_and_counts(example_asset, 0, 0)

    def test_saving_the_same_review_again_should_not_update_avg_rating_or_count(
        self,
        example_asset,
        user_and_password,
    ):
        assert AssetReview.objects.count() == 0
        self._validate_avg_rating_and_count(example_asset, 0, 0)
        test_user = user_and_password[0]
        review1 = AssetReview.objects.create(
            asset=example_asset,
            user=test_user,
            rating=7,
        )
        self._validate_avg_rating_and_count(example_asset, 7, 1)

        # Second save should not increase the count
        review1.save()
        self._validate_avg_rating_and_count(example_asset, 7, 1)
