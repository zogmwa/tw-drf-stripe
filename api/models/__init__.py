from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .asset import Asset
from .tag import Tag
from .user import User
from .price_plan import PricePlan
from .asset_attribute import Attribute
from .linked_attribute import LinkedAttribute
from .asset_question import AssetQuestion
from .asset_vote import AssetVote
from .linked_tag import LinkedTag
from .attribute_vote import AttributeVote
from .linked_attribute import LinkedAttribute


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def get_anonymous_user_instance(user_class):
    """
    Added just to comply with: https://django-guardian.readthedocs.io/en/stable/userguide/custom-user-model.html
    """
    return user_class(username='AnonymousUser')
