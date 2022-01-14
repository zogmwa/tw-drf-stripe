from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .asset import Asset
from .solution import Solution
from .tag import Tag
from .user import User
from .price_plan import PricePlan
from .asset_attribute import Attribute
from .linked_attribute import LinkedAttribute
from .asset_question import AssetQuestion
from .asset_question_vote import AssetQuestionVote
from .asset_vote import AssetVote
from .linked_solution import LinkedSolution
from .linked_tag import LinkedTag
from .asset_attribute_vote import AssetAttributeVote
from .linked_attribute import LinkedAttribute
from .asset_review import AssetReview
from .organization import Organization
from .organization import OrganizationUsingAsset
from .claim_asset import AssetClaim
from .user_asset_usage import UserAssetUsage
from .asset_snapshot import AssetSnapshot
from .linked_solution_tag import LinkedSolutionTag
from .solution_vote import SolutionVote
from .solution_question import SolutionQuestion
from .solution_bookmark import SolutionBookmark
from .newsletter_contact import NewsLetterContact
from .solution_review import SolutionReview
from .webhooks_stripe import product_created_handler, price_created_handler
from .submitted_problem import SubmittedProblem


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def get_anonymous_user_instance(user_class):
    """
    Added just to comply with: https://django-guardian.readthedocs.io/en/stable/userguide/custom-user-model.html
    """
    return user_class(username='AnonymousUser')
