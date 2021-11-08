import pytest
from django.test import Client

from api.models import (
    Asset,
    User,
    Tag,
    Attribute,
    AssetAttributeVote,
    AssetQuestionVote,
    AssetSnapshot,
    PricePlan,
)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(autouse=True)
def patch_elasticsearch(mocker):
    # Patch elasticsearch so that whenever a db save happens an elastic search index update request does not fail
    # in the tests. Later on figure out how to patch this in a better way with some data so that we can still have a
    # mock index that can be used for testing search flows.
    mocker.patch('elasticsearch.Transport.perform_request')


@pytest.fixture
def example_asset():
    return Asset.objects.create(
        slug='mailchimp',
        name='Mailchimp',
        website='https://mailchimp.com/',
        short_description='bla bla',
        description='bla bla bla',
        promo_video='https://www.youtube.com/embed/Q0hi9d1W3Ag',
        is_published=True,
    )


@pytest.fixture
def example_asset_2():
    return Asset.objects.create(
        slug='test-service-2',
        name='Test Service 2',
        is_published=True,
    )


@pytest.fixture
def example_asset_3():
    return Asset.objects.create(
        slug='test-service-3',
        name='Test Service 3',
        is_published=True,
    )


@pytest.fixture
def example_asset_4():
    return Asset.objects.create(
        slug='test-service-4',
        name='Test Service 4',
        is_published=True,
    )


@pytest.fixture
def example_featured_asset():
    return Asset.objects.create(
        slug='featured_asset',
        name='Featured Asset',
        is_homepage_featured=True,
    )


@pytest.fixture
def example_attribute(example_asset):
    return Attribute.objects.create(name='Test Attribute')


@pytest.fixture
def example_asset_attribute(example_asset):
    return example_asset.attributes.create(name='Test Asset Attribute')


@pytest.fixture
def example_asset_question(example_asset):
    return example_asset.questions.create(title='Test Asset Question')


@pytest.fixture
def example_asset_attribute_vote(
    user_and_password, example_asset, example_asset_attribute
):
    user = user_and_password[0]
    return AssetAttributeVote.objects.create(
        user=user, asset=example_asset, attribute=example_asset_attribute
    )


@pytest.fixture
def example_asset_question_vote(user_and_password, example_asset_question):
    user = user_and_password[0]
    return AssetQuestionVote.objects.create(user=user, question=example_asset_question)


@pytest.fixture
def example_tag():
    return Tag.objects.create(slug='tag', name='tag_name')


@pytest.fixture
def example_featured_tag():
    return Tag.objects.create(
        slug='featured_tag', name='Featured Tag', is_homepage_featured=True
    )


@pytest.fixture
def user_and_password():
    username = 'username'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user, password


@pytest.fixture
def user_and_password_2():
    username = 'username2'
    password = 'password2'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user, password


@pytest.fixture
def admin_user_and_password():
    username = 'admin'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.save()
    return user, password


@pytest.fixture
def staff_user_and_password():
    username = 'staff'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.is_staff = True
    user.save()
    return user, password


@pytest.fixture()
def authenticated_client(user_and_password):
    """
    If you need the corresponding user which this authenticated_client represents check user_and_password fixture"
    """
    client = Client()
    client.login(username=user_and_password[0].username, password=user_and_password[1])
    assert client.session['_auth_user_id'] == str(user_and_password[0].id)
    return client


@pytest.fixture()
def authenticated_client_2(user_and_password_2):
    """
    If you need the corresponding user which this authenticated_client represents check user_and_password fixture"
    """
    client = Client()
    client.login(
        username=user_and_password_2[0].username, password=user_and_password_2[1]
    )
    assert client.session['_auth_user_id'] == str(user_and_password_2[0].id)
    return client


@pytest.fixture()
def unauthenticated_client():
    client = Client()
    return client


@pytest.fixture()
def example_snapshot(example_asset):
    return AssetSnapshot.objects.create(
        asset=example_asset,
        url='https://eep.io/images/yzco4xsimv0y/2N9sFG6PG9HDHwJ4mtvS7k/19f56d3cdae2403d604e65f4b3db3ce7/00_-_Hero.png',
    )


@pytest.fixture()
def example_price_plan(example_asset):
    return PricePlan.objects.create(
        asset=example_asset,
        name="standard",
        summary="standard",
        currency="USD",
    )
