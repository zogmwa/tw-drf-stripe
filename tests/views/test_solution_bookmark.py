import pytest
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from api.models import SolutionBookmark

SOLUTION_BOOKMARKS_ENDPOINT = 'http://127.0.0.1:8000/solution_bookmarks/'


class TestSolutionBookmark:
    def test_fetch_solution_bookmark(
        self,
        unauthenticated_client,
        authenticated_client,
        user_and_password,
        example_solution,
    ):
        # Fetch solution bookmarks with unauthenticated user
        solution_bookmark_to_be_fetch = SolutionBookmark.objects.create(
            solution=example_solution, user=user_and_password[0]
        )
        response = unauthenticated_client.get(SOLUTION_BOOKMARKS_ENDPOINT)

        assert response.status_code == 401

        # Fetch solution bookmarks with authenticated user
        response = authenticated_client.get(SOLUTION_BOOKMARKS_ENDPOINT)

        assert response.status_code == 200
        assert (
            response.data[0]['solution']['id']
            == solution_bookmark_to_be_fetch.solution.id
        )
        assert response.data[0]['user'] == user_and_password[0].id

    def test_solution_bookmark_create(
        self,
        unauthenticated_client,
        authenticated_client,
        user_and_password,
        example_solution,
    ):
        # Bookmark on solution with unauthenticated user
        response = unauthenticated_client.post(
            SOLUTION_BOOKMARKS_ENDPOINT,
            {
                'solution': example_solution.id,
            },
        )
        assert response.status_code == 401

        # Bookmark on solution with authenticated user
        response = authenticated_client.post(
            SOLUTION_BOOKMARKS_ENDPOINT,
            {
                'solution': example_solution.id,
            },
        )
        assert response.status_code == HTTP_200_OK
        solution_bookmark = SolutionBookmark.objects.get()
        assert solution_bookmark.user.id == user_and_password[0].id

    def test_solution_bookmark_delete(
        self,
        unauthenticated_client,
        authenticated_client,
        user_and_password,
        example_solution,
    ):
        # Cancel Bookmark with unauthenticated user
        solution_bookmark_to_be_deleted = SolutionBookmark.objects.create(
            solution=example_solution, user=user_and_password[0]
        )

        solution_bookmark_detail_endpoint = "{}{}/".format(
            SOLUTION_BOOKMARKS_ENDPOINT, solution_bookmark_to_be_deleted.id
        )
        get_solution_bookmarks_response = unauthenticated_client.get(
            solution_bookmark_detail_endpoint
        )

        assert get_solution_bookmarks_response.status_code == 401

        # Cancel Bookmark on solution with authenticated user
        solution_bookmark_detail_endpoint = "{}{}/".format(
            SOLUTION_BOOKMARKS_ENDPOINT, solution_bookmark_to_be_deleted.id
        )
        get_solution_bookmarks_response = authenticated_client.get(
            solution_bookmark_detail_endpoint
        )
        assert get_solution_bookmarks_response.status_code == HTTP_200_OK

        # Cancel Bookmark on solution
        response = authenticated_client.delete(
            solution_bookmark_detail_endpoint,
            {
                'solution': example_solution.id,
            },
            content_type='application/json',
        )
        assert response.status_code == HTTP_204_NO_CONTENT
