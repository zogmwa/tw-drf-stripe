from django.test import Client


def login_client(user_and_password):
    client = Client()
    client.login(username=user_and_password[0].username, password=user_and_password[1])
    assert client.session['_auth_user_id'] == str(user_and_password[0].id)
    return client
