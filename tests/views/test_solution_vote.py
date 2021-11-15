import pytest
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from api.models import SolutionVote

SOLUTION_VOTES_ENDPOINT = 'http://127.0.0.1:8000/solution_votes/'


class TestSolutionVote:
    def test_create_with_logged_in_user(
        self,
        authenticated_client,
        user_and_password,
        example_solution,
    ):
        # Vote on solution
        response = authenticated_client.post(
            SOLUTION_VOTES_ENDPOINT,
            {
                'solution': example_solution.id,
            },
        )
        assert response.status_code == HTTP_200_OK
        solution_vote = SolutionVote.objects.get()
        assert solution_vote.user.id == user_and_password[0].id

    def test_get_and_delete(
        self,
        authenticated_client,
        user_and_password,
        example_solution,
    ):
        solution_vote_to_be_deleted = SolutionVote.objects.create(
            solution=example_solution, user=user_and_password[0]
        )

        solution_vote_detail_endpoint = "{}{}/".format(
            SOLUTION_VOTES_ENDPOINT, solution_vote_to_be_deleted.id
        )
        get_solution_votes_response = authenticated_client.get(
            solution_vote_detail_endpoint
        )
        assert get_solution_votes_response.status_code == HTTP_200_OK
        assert get_solution_votes_response.data['id'] == solution_vote_to_be_deleted.id

        # Cancel vote on solution
        response = authenticated_client.delete(
            solution_vote_detail_endpoint,
            {
                'solution': example_solution.id,
            },
            content_type='application/json',
        )
        assert response.status_code == HTTP_204_NO_CONTENT
