import pytest
from django.db import IntegrityError

from api.models import AssetReview


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
