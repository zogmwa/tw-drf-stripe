import pytest
from api.models import AssetQuestion, AssetQuestionVote, Asset


def test_asset_question_is_unique_for_asset(example_asset, user_and_password):

    question1 = AssetQuestion.objects.create(
        asset=example_asset,
        title="Sample Question",
        primary_answer="Sample Answer",
    )
    question1.save()

    def _check_upvote_counts_of_a_question(expected_count: int) -> None:
        assert (
            Asset.objects.get(id=example_asset.id)
            .questions.get(id=question1.id)
            .upvotes_count
            == expected_count
        )

    _check_upvote_counts_of_a_question(0)
    question_vote1 = AssetQuestionVote.objects.create(
        is_upvote=True, question=question1, user=user_and_password[0]
    )
    question_vote1.save()
    _check_upvote_counts_of_a_question(1)

    # question_vote2 = AssetQuestionVote.objects.create(
    # is_upvote=True, question=question1, user=user_and_password[0]
    # )
    question_vote1.save()
    _check_upvote_counts_of_a_question(1)

    question_vote1.delete()
    _check_upvote_counts_of_a_question(0)
