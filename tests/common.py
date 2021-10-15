from django.test import Client
import string, random


def login_client(user_and_password):
    client = Client()
    client.login(username=user_and_password[0].username, password=user_and_password[1])
    assert client.session['_auth_user_id'] == str(user_and_password[0].id)
    return client


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
