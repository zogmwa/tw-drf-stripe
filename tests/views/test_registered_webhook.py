import pytest
from api.models.registered_webhook import RegisteredWebhook

REGISTERED_WEBHOOK_ENDPOINT = 'http://127.0.0.1:8000/registered_webhook/'
ATTACH_EVENT_NAME = 'payment_method.attach'
DETACH_EVENT_NAME = 'payment_method.detach'
TEST_RECEIVER_URL = 'http://127.0.0.1/'


class TestRegisteredWebhook:
    def test_authenticated_user_could_create_registered_webhook(
        self, authenticated_client
    ):
        response = authenticated_client.post(
            REGISTERED_WEBHOOK_ENDPOINT,
            {
                'event_name': 'payment_method.attach',
                'receiver_url': 'http://127.0.0.1/',
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.data['event_name'] == ATTACH_EVENT_NAME
        assert response.data['receiver_url'] == TEST_RECEIVER_URL
