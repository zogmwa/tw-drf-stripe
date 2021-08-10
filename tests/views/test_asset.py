from api.models import Asset, User
from django.test.client import Client
import pytest


@pytest.fixture()
def user_and_password():
    username = 'username'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user, password


def check_login_user(user_and_password):
    client = Client()
    client.login(username=user_and_password[0].username, password=user_and_password[1])
    assert client.session['_auth_user_id'] == str(user_and_password[0].id)
    return client


def test_submitted_by_is_set_to_logged_in_user_when_saving_asset(user_and_password):
    # Create a mock request with the user object set (simulating a logged in user)
    asset_url = 'http://127.0.0.1:8000/assets/'
    asset_slug = 'test_slug'
    asset_name = 'test_asset'
    asset_description = 'Some test description'
    asset_short_description = 'short description of asset'

    client = check_login_user(user_and_password)
    response = client.post(asset_url, {'slug': asset_slug, 'name': asset_name, 'description': asset_description,
                                       'short_description': asset_short_description})
    assert response.status_code == 201

    asset = Asset.objects.get(slug=asset_slug)
    assert asset.submitted_by == user_and_password[0]
