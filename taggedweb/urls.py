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

from api.auth_views import GoogleLogin
from api.views import AssetViewSet, autocomplete_tags, AssetQuestionViewSet, AssetClickThroughCounterRedirectView, \
    AssetVoteViewSet, UserViewSet
from dj_rest_auth.views import PasswordResetConfirmView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'questions', AssetQuestionViewSet)
router.register(r'upvotes', AssetVoteViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('autocomplete-tags/', autocomplete_tags),

    # DRF Standard Token Auth Views
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),

    # Authentication
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('accounts/', include('allauth.urls')),

    # DRF JWT Token Views (Preferable over Standard Tokens as these are more performant as they don't involve the db)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path(
        'r/assets/<slug:slug>',
        AssetClickThroughCounterRedirectView.as_view(),
        name='asset_clickthrough_counter_redirect_view',
    ),
]
