from api.models import AssetReview


def test_review_user_is_set_to_logged_in_user_when_adding_a_new_review(
        user_and_password, authenticated_client, example_asset
):
    asset_reviews_url = 'http://127.0.0.1:8000/asset_reviews/'
    response = authenticated_client.post(
        asset_reviews_url,
        {
            'asset': example_asset.id,
            'content': 'Test review',
            'rating': 9,
        }
    )
    assert response.status_code == 201

    review = AssetReview.objects.get(asset=example_asset)
    assert review.user == user_and_password[0]
