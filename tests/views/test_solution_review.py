import pytest

from api.models import Solution
from api.models import SolutionReview

from api.views.solutions import SolutionViewSet

SOLUTION_REVIEWS_ENDPOINT = 'http://127.0.0.1:8000/solution_reviews/'
SOLUTIONS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solutions/'


class TestSolutionReview:
    def test_solution_review_create_with_logged_in_user(
        self,
        unauthenticated_client,
        authenticated_client,
        user_and_password,
        example_solution,
        mocker,
    ):
        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.all(),
        )

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

        # unauthenticated user couldn't fetch my_solution_review field
        solution_list_url = '{}?q={}'.format(SOLUTIONS_BASE_ENDPOINT, 'Test')
        response = unauthenticated_client.get(solution_list_url)

        assert 'my_solution_review' not in response.data['results'][0].keys()
        assert response.data['results'][0]['sad_count'] == 1

        # authenticated user could fetch my_solution_review field and sad_count
        response = authenticated_client.get(solution_list_url)

        assert (
            response.data['results'][0]['my_solution_review'] == SolutionReview.Type.SAD
        )
        assert response.data['results'][0]['sad_count'] == 1
        assert response.data['results'][0]['happy_count'] == 0
        assert response.data['results'][0]['neutral_count'] == 0

        # Re submit solution review with another type status and same authenticated user
        response = authenticated_client.post(
            SOLUTION_REVIEWS_ENDPOINT,
            {'solution': example_solution.id, 'type': SolutionReview.Type.HAPPY},
        )
        assert response.status_code == 200
        assert response.data['solution']['id'] == example_solution.id
        assert response.data['type'] == SolutionReview.Type.HAPPY

        # authenticated user could fetch my_solution_review field and sad_count
        response = authenticated_client.get(solution_list_url)

        assert (
            response.data['results'][0]['my_solution_review']
            == SolutionReview.Type.HAPPY
        )
        assert response.data['results'][0]['sad_count'] == 0
        assert response.data['results'][0]['happy_count'] == 1
        assert response.data['results'][0]['neutral_count'] == 0

        # Resubmit solution review with same type status and same authenticated user
        response = authenticated_client.post(
            SOLUTION_REVIEWS_ENDPOINT,
            {'solution': example_solution.id, 'type': SolutionReview.Type.HAPPY},
        )
        assert response.status_code == 200

        # There will be any solution reviews
        response = authenticated_client.get(SOLUTION_REVIEWS_ENDPOINT)

        assert response.status_code == 200
        assert len(response.data) == 0

        response = authenticated_client.get(solution_list_url)

        assert response.data['results'][0]['my_solution_review'] == None
        assert response.data['results'][0]['sad_count'] == 0
        assert response.data['results'][0]['happy_count'] == 0
        assert response.data['results'][0]['neutral_count'] == 0
