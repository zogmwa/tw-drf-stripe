from api.models import Asset, AssetVote


def test_upvotes_count_for_an_asset_should_be_updated_automatically_if_asset_vote_is_created_update_deleted(
    user_and_password,
    authenticated_client,
    example_asset,
):
    def _check_upvote_counts_of_an_asset(expected_count: int) -> None:
        assert Asset.objects.get(id=example_asset.id).upvotes_count == expected_count

    _check_upvote_counts_of_an_asset(0)

    asset_vote = AssetVote.objects.create(
        is_upvote=False, asset_id=example_asset.id, user_id=user_and_password[0].id
    )
    _check_upvote_counts_of_an_asset(0)

    asset_vote.is_upvote = True
    asset_vote.save()
    _check_upvote_counts_of_an_asset(1)

    asset_vote.is_upvote = True
    asset_vote.save()
    _check_upvote_counts_of_an_asset(1)
