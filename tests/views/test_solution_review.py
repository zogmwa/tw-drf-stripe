import pytest
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from api.models import SolutionReview

SOLUTION_REVIEWS_ENDPOINT = 'http://127.0.0.1:8000/solution_reviews/'


class TestSolutionReview:
    def test_solution_review_create_with_logged_in_user(
        self,
        unauthenticated_client,
        authenticated_client,
        user_and_password,
        example_solution,
    ):
        # Create solution review with unauthenticated user
        response = unauthenticated_client.post(
            SOLUTION_REVIEWS_ENDPOINT,
            {'solution': example_solution.id, 'type': SolutionReview.Type.SAD},
        )
        assert response.status_code == 401

        # Create solution review with authenticated user
        response = authenticated_client.post(
            SOLUTION_REVIEWS_ENDPOINT,
            {'solution': example_solution.id, 'type': SolutionReview.Type.SAD},
        )
        assert response.status_code == 200
        assert response.data['solution']['id'] == example_solution.id
        assert response.data['type'] == SolutionReview.Type.SAD

        # Re submit solution review with another type status and same authenticated user
        response = authenticated_client.post(
            SOLUTION_REVIEWS_ENDPOINT,
            {'solution': example_solution.id, 'type': SolutionReview.Type.HAPPY},
        )
        assert response.status_code == 200
        assert response.data['solution']['id'] == example_solution.id
        assert response.data['type'] == SolutionReview.Type.HAPPY

        # Re submit solution review with same type status and same authenticated user
        response = authenticated_client.post(
            SOLUTION_REVIEWS_ENDPOINT,
            {'solution': example_solution.id, 'type': SolutionReview.Type.HAPPY},
        )
        assert response.status_code == 200
        assert response.data['solution']['id'] == example_solution.id
        assert response.data['type'] == SolutionReview.Type.HAPPY
