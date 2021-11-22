import pytest

NEWSLETTER_BASE_ENDPOINT = 'http://127.0.0.1:8000/newsletter_contact/'


def test_newsletter_contact_create(unauthenticated_client):

    response = unauthenticated_client.post(
        NEWSLETTER_BASE_ENDPOINT, {"email": "test@example.com"}
    )
    assert response.json() != None
    assert response.status_code == 201


def test_newsletter_incorrect_email(unauthenticated_client):
    response1 = unauthenticated_client.post(
        NEWSLETTER_BASE_ENDPOINT, {"email": "testexample.com"}
    )
    response2 = unauthenticated_client.post(
        NEWSLETTER_BASE_ENDPOINT, {"email": "test@examplecom"}
    )
    response3 = unauthenticated_client.post(
        NEWSLETTER_BASE_ENDPOINT, {"email": "testexamplecom"}
    )

    assert (
        response1.json() != None
        and response2.json() != None
        and response3.json() != None
    )
    assert (
        response1.status_code == 400
        and response2.status_code == 400
        and response3.status_code == 400
    )


def test_newsletter_empty_email_field(unauthenticated_client):

    response = unauthenticated_client.post(NEWSLETTER_BASE_ENDPOINT, {"email": ""})

    assert response.json() != None
    assert response.status_code == 400
