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

from api.views.asset_attribute_votes import AssetAttributeVoteViewSet
from api.views.asset_reviews import AssetReviewViewSet
from api.views.auth import GoogleLogin, LinkedInLogin
from api.views.asset import AssetViewSet
from api.views.asset_attributes import AssetAttributeViewSet
from api.views.common import autocomplete_tags, autocomplete_assets_and_tags

from api.views.asset_questions import AssetQuestionViewSet
from api.views.analytics import AssetClickThroughCounterRedirectView
from api.views.asset_votes import AssetVoteViewSet
from dj_rest_auth.views import PasswordResetConfirmView

from api.views.price_plans import PricePlanViewSet
from api.views.user import UserViewSet

# Swagger code starts here
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
router.register(r'assets', AssetViewSet)
router.register(r'questions', AssetQuestionViewSet)
router.register(r'price_plans', PricePlanViewSet)
router.register(r'upvotes', AssetVoteViewSet)
router.register(r'asset_attributes', AssetAttributeViewSet)
router.register(r'asset_attribute_votes', AssetAttributeVoteViewSet)

# E.g. To filter ratings where asset__slug=makemymails and rating is 10
# GET: /asset_reviews/?asset__slug=makemymails&rating=10
router.register(r'asset_reviews', AssetReviewViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # swaggerAPI
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
    # DRF Standard Token Auth Views
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),
    # Authentication
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # Social Authentication
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    # https://django-allauth.readthedocs.io/en/latest/providers.html?highlight=LinkedIn#linkedin
    path('dj-rest-auth/linkedin/', LinkedInLogin.as_view(), name='linkedin_login'),
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
]
