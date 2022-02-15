import pytest

from api.models import solution

CONSULTATION_REQUEST_ENDPOINT = "http://127.0.0.1:8000/consultation_request/"


@pytest.fixture
def consultation_request_user_data():
    return {
        "customer_email": "user@email.com",
        "customer_first_name": "first_name",
        "customer_last_name": "last_name",
    }


@pytest.fixture
def consultation_request_user2_data():
    return {
        "customer_email": "user2@email.com",
        "customer_first_name": "first_name2",
        "customer_last_name": "last_name2",
    }


@pytest.fixture
def consultation_request_response(
    unauthenticated_client, consultation_request_user_data, example_solution
):
    response = unauthenticated_client.post(
        CONSULTATION_REQUEST_ENDPOINT,
        {"solution": example_solution.id, **consultation_request_user_data},
    )
    assert response.status_code == 201
    return response


class TestConsultationRequest:
    def test_create_action_consultation_request(
        self, unauthenticated_client, consultation_request_user_data, example_solution
    ):
        response = unauthenticated_client.post(
            CONSULTATION_REQUEST_ENDPOINT,
            {"solution": example_solution.id, **consultation_request_user_data},
        )
        assert response.status_code == 201

    def test_retrieve_action_consultation_request(
        self, unauthenticated_client, consultation_request_response
    ):
        response = unauthenticated_client.get(
            f"{CONSULTATION_REQUEST_ENDPOINT}{consultation_request_response.data['id']}/",
        )
        assert response.status_code == 200
