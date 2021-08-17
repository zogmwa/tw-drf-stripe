import pytest

from api.models import Asset, User


@pytest.fixture
def example_asset():
    return Asset.objects.create(
        slug='mailchimp',
        name='Mailchimp',
        website='https://mailchimp.com/',
        short_description='bla bla',
        description='bla bla bla',
        promo_video='https://www.youtube.com/embed/Q0hi9d1W3Ag',
    )


@pytest.fixture
def user_and_password():
    username = 'username'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user, password
