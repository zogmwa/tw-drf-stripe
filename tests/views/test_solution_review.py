import pytest

from api.models import Solution
from api.models import SolutionReview

from api.views.solutions import SolutionViewSet

SOLUTION_REVIEWS_ENDPOINT = 'http://127.0.0.1:8000/solution_reviews/'
SOLUTIONS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solutions/'
solution_list_url = '{}?q={}'.format(SOLUTIONS_BASE_ENDPOINT, 'Test')


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
        assert response.status_code == 201
        assert response.data['type'] == SolutionReview.Type.SAD
        assert response.data['solution_avg_rating'] == -1

        # unauthenticated user couldn't fetch my_solution_review field
        response = unauthenticated_client.get(solution_list_url)

        assert 'my_solution_review' not in response.data['results'][0].keys()
        assert response.data['results'][0]['avg_rating'] == -1

        # authenticated user could fetch my_solution_review field and sad_count
        response = authenticated_client.get(solution_list_url)

        assert (
            response.data['results'][0]['my_solution_review'] == SolutionReview.Type.SAD
        )
        assert response.data['results'][0]['avg_rating'] == -1

    def test_solution_review_update_with_logged_in_user(
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

        solution_review = SolutionReview.objects.create(
            solution=example_solution, user=user_and_password[0]
        )
        # Authenticated user could update solution review.
        response = authenticated_client.patch(
            '{}{}/'.format(SOLUTION_REVIEWS_ENDPOINT, solution_review.id),
            {
                'solution': example_solution.id,
                'type': SolutionReview.Type.HAPPY,
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.data['type'] == SolutionReview.Type.HAPPY
        assert response.data['solution_avg_rating'] == 1

        # authenticated user could fetch my_solution_review field and sad_count
        response = authenticated_client.get(solution_list_url)

        assert (
            response.data['results'][0]['my_solution_review']
            == SolutionReview.Type.HAPPY
        )
        assert response.data['results'][0]['avg_rating'] == 1

    def test_solution_review_delete_with_logged_in_user(
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

        solution_review = SolutionReview.objects.create(
            solution=example_solution, user=user_and_password[0]
        )
        # Authenticated user could delete solution review.
        response = authenticated_client.delete(
            '{}{}/'.format(SOLUTION_REVIEWS_ENDPOINT, solution_review.id)
        )
        assert response.status_code == 204

        # There will be any solution reviews
        response = authenticated_client.get(SOLUTION_REVIEWS_ENDPOINT)

        assert response.status_code == 200
        assert len(response.data) == 0

        response = authenticated_client.get(solution_list_url)

        assert response.data['results'][0]['my_solution_review'] == None
        assert response.data['results'][0]['avg_rating'] == 0
