import pytest

DJ_REST_AUTH_BASE_ENDPOINT = 'http://127.0.0.1:8000/dj-rest-auth/registration/'


def test_user_create_using_djrestauth(unauthenticated_client):

    response = unauthenticated_client.post(
        DJ_REST_AUTH_BASE_ENDPOINT,
        {
            "email": "test@example.com",
            "password1": "Test#123",
            "password2": "Test#123",
            "first_name": "taggedweb",
            "last_name": "test",
        },
    )

    assert response.json() != None
    assert response.json()['user']["username"] != ""
    assert response.status_code == 201


def test_user_create_with_empty_email_field(unauthenticated_client):

    response = unauthenticated_client.post(
        DJ_REST_AUTH_BASE_ENDPOINT,
        {
            "email": "",
            "password1": "Test#123",
            "password2": "Test#123",
            "first_name": "taggedweb",
            "last_name": "test",
        },
    )
    assert response.json() != None
    assert response.status_code == 400


def test_user_create_with_different_password_field(unauthenticated_client):

    response = unauthenticated_client.post(
        DJ_REST_AUTH_BASE_ENDPOINT,
        {
            "email": "test@example.com",
            "password1": "Test#123",
            "password2": "Test#124",
            "first_name": "taggedweb",
            "last_name": "test",
        },
    )
    assert response.json() != None
    assert response.status_code == 400
