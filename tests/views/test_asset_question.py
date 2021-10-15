from rest_framework import status

from api.models import Asset, Tag
import pytest
from django.test import Client

from api.models.asset_snapshot import AssetSnapshot

from api.views.asset import AssetViewSet
from tests.common import login_client
from pytest_lazyfixture import lazy_fixture


ASSET_QUESTIONS_ENDPOINT = 'http://127.0.0.1:8000/questions/'
ASSET_QUESTION_VOTES_ENDPOINT = 'http://127.0.0.1:8000/question_votes/'


class TestAssetQuestionVotedByMe:
    def test_for_anonymous_user_my_asset_question_vote_field_should_not_be_passed_in_response_of_list_or_for_a_single_asset(
        self, unauthenticated_client, example_asset_question
    ):

        response = unauthenticated_client.get(ASSET_QUESTIONS_ENDPOINT)
        assert response.status_code == 200
        assert 'my_asset_question_vote' not in response.data[0].keys()

        asset_question_url = '{}{}/'.format(
            ASSET_QUESTIONS_ENDPOINT, example_asset_question.id
        )
        response = unauthenticated_client.get(asset_question_url)
        assert response.status_code == 200
        assert response.data['id'] == example_asset_question.id
        assert 'my_asset_question_vote' not in response.data.keys()

    @pytest.mark.parametrize("is_asset_question_voted", [True, False])
    def test_for_logged_in_user_my_asset_question_vote_field_should_be_returned_and_show_correct_value(
        self,
        authenticated_client,
        example_asset_question,
        example_asset_question_vote,
        is_asset_question_voted,
        user_and_password,
    ):
        if not is_asset_question_voted:
            response = authenticated_client.delete(
                '{}{}/'.format(
                    ASSET_QUESTION_VOTES_ENDPOINT, example_asset_question_vote.id
                )
            )
            assert response.status_code == 204

        # Get questions list
        response = authenticated_client.get(ASSET_QUESTIONS_ENDPOINT)
        assert response.status_code == 200

        if is_asset_question_voted:
            assert (
                response.data[0]['my_asset_question_vote']
                == example_asset_question_vote.id
            )
        else:
            assert response.data[0]['my_asset_question_vote'] is None

        # Get question detail
        asset_question_url = '{}{}/'.format(
            ASSET_QUESTIONS_ENDPOINT, example_asset_question.id
        )
        response = authenticated_client.get(asset_question_url)
        assert response.status_code == 200

        if is_asset_question_voted:
            assert (
                response.data['my_asset_question_vote']
                == example_asset_question_vote.id
            )
        else:
            assert response.data['my_asset_question_vote'] is None
