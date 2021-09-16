import requests
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.provider import (
    LinkedInOAuth2Provider,
)
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView, SocialConnectView
from django.http import JsonResponse


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter


class LinkedInLogin(SocialLoginView):
    adapter_class = LinkedInOAuth2Adapter


class LinkedInConnect(SocialConnectView):
    adapter_class = LinkedInOAuth2Adapter


def linkedin_oauth2_access_token_from_auth_code(request):
    code_param = 'code'
    redirect_uri_param = 'redirect_uri'

    auth_code = request.POST.get(code_param) or request.GET.get(code_param)
    redirect_uri = request.POST.get(redirect_uri_param) or request.GET.get(
        redirect_uri_param
    )

    data = {
        "error": "invalid_request",
    }
    status_code = 422

    if not auth_code:
        data["error_description"] = "A required parameter \"code\" is missing"
    elif not redirect_uri:
        data["error_description"] = "A required parameter \"redirect_uri\" is missing"
    else:
        linkedin_app = SocialApp.objects.get(provider=LinkedInOAuth2Provider.id)
        client_id = linkedin_app.client_id
        client_secret = linkedin_app.secret
        linkedin_access_token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        grant_type = 'authorization_code'

        # https://docs.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow?context=linkedin%2Fcontext&tabs=HTTPS#step-3-exchange-authorization-code-for-an-access-token
        linkedin_auth_token_data = {
            'grant_type': grant_type,
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(
            url=linkedin_access_token_url,
            data=linkedin_auth_token_data,
            headers=headers,
        )
        status_code = response.status_code
        data = response.json()
        data['redirect_uri'] = redirect_uri
        data['client_id'] = client_id
    return JsonResponse(data, status=status_code)
