"""taggedweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views.newsletter_contact import NewsLetterContactViewSet
from api.views.asset_attribute_votes import AssetAttributeVoteViewSet
from api.views.asset_reviews import AssetReviewViewSet
from api.views.solution_reviews import SolutionReviewViewSet
from payments.views import CreateStripeCheckoutSession
from api.views.solution_bookings import SolutionBookingViewSet
from api.views.solutions import SolutionViewSet, autocomplete_solutions
from api.views.solution_questions import autocomplete_solution_questions
from api.views.solution_votes import SolutionVoteViewSet
from api.views.solution_bookmarks import SolutionBookmarkViewSet
from api.views.auth import (
    GoogleLogin,
    LinkedInLogin,
    linkedin_oauth2_access_token_from_auth_code,
    LinkedInConnect,
    GoogleConnect,
)
from api.views.asset import AssetViewSet
from api.views.asset_attributes import AssetAttributeViewSet, autocomplete_attributes
from api.views.tag import autocomplete_tags, autocomplete_assets_and_tags, TagViewSet
from api.views.asset_questions import AssetQuestionViewSet
from api.views.asset_question_votes import AssetQuestionVoteViewSet
from api.views.analytics import AssetClickThroughCounterRedirectView
from api.views.asset_votes import AssetVoteViewSet
from api.views.asset_claims import AssetClaimViewSet
from api.views.download_sitemap import download_sitemap
from dj_rest_auth.views import PasswordResetConfirmView
from api.views.user_problem import UserProblemViewSet
from api.views.organization import autocomplete_organizations
from api.views.price_plans import PricePlanViewSet
from api.views.user import UserViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="TaggedWeb API",
        default_version='v1',
        description="Welcome to the world of TaggedWeb Backend",
        terms_of_service="https://www.taggedweb.com",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    permission_classes=(permissions.IsAdminUser,),
)
# ends here

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'questions', AssetQuestionViewSet)
router.register(r'question_votes', AssetQuestionVoteViewSet)
router.register(r'price_plans', PricePlanViewSet)
router.register(r'asset_votes', AssetVoteViewSet)
router.register(r'asset_attributes', AssetAttributeViewSet)
router.register(r'asset_attribute_votes', AssetAttributeVoteViewSet)
router.register(r'asset_claims', AssetClaimViewSet)
# E.g. To filter ratings where asset__slug=makemymails and rating is 10
# GET: /asset_reviews/?asset__slug=makemymails&rating=10
router.register(r'asset_reviews', AssetReviewViewSet)
router.register(r'solution_reviews', SolutionReviewViewSet)
router.register(r'solutions', SolutionViewSet)
router.register(r'solution_bookings', SolutionBookingViewSet)
router.register(r'solution_bookmarks', SolutionBookmarkViewSet)
router.register(r'solution_votes', SolutionVoteViewSet)
router.register(r'newsletter_contact', NewsLetterContactViewSet)
router.register(r'user_problems', UserProblemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path(
        'docs/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
    # (Deprecated): Replace this by `autocomplete-tags-and-assets` on the frontend.
    path('autocomplete-tags/', autocomplete_tags),
    # This endpoint suggests both tags and assets. Response for a query like `/autocomplete-tags-and-assets/?q=ac` is:
    # {
    #   "tags": [
    #     "accounting"
    #   ],
    #   "assets": [
    #     "Accern",
    #     "Acobot",
    #     "Actionable Science"
    #   ]
    # }
    path('autocomplete-tags-and-assets/', autocomplete_assets_and_tags),
    path('autocomplete-attributes/', autocomplete_attributes),
    path('autocomplete-organizations/', autocomplete_organizations),
    path('autocomplete-solutions/', autocomplete_solutions),
    path('autocomplete-solution-questions/', autocomplete_solution_questions),
    # Download sitemap file
    path('download/sitemap/', download_sitemap),
    # DRF Standard Token Auth Views
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),
    # Authentication
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # Social Authentication
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path(
        'dj-rest-auth/google/connect/',
        GoogleConnect.as_view(),
        name='google_connect',
    ),
    # Tweb endpint to allow a frontend app to exchange auth-code for a LinkedIn authtoken
    path(
        'tweb-auth/linkedin/authtoken-from-code',
        linkedin_oauth2_access_token_from_auth_code,
        name='linkedin_auth_token',
    ),
    # https://django-allauth.readthedocs.io/en/latest/providers.html?highlight=LinkedIn#linkedin
    # Exchange LinkedIn Auth token, code, client_id for TaggedWeb auth_token
    path('dj-rest-auth/linkedin/', LinkedInLogin.as_view(), name='linkedin_login'),
    path(
        'dj-rest-auth/linkedin/connect/',
        LinkedInConnect.as_view(),
        name='linkedin_connect',
    ),
    path(
        'password/reset/confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path('accounts/', include('allauth.urls')),
    # DRF JWT Token Views (Preferable over Standard Tokens as these are more performant as they don't involve the db)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # For links clickthrough counts
    path(
        'r/assets/<slug:slug>',
        AssetClickThroughCounterRedirectView.as_view(),
        name='asset_clickthrough_counter_redirect_view',
    ),
    # Payments
    path('stripe/', include('djstripe.urls', namespace='djstripe')),
    path(
        'solution-price-checkout/<str:pay_now_stripe_price_id>',
        CreateStripeCheckoutSession.as_view(),
        name='create_stripe_checkout_session',
    ),
]
