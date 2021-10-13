from dj_rest_auth.serializers import PasswordResetSerializer as _PasswordResetSerializer
from django.contrib.auth.forms import PasswordResetForm


class PasswordResetSerializer(_PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        # AllAuthPasswordResetForm that dj-rest-auth delegates to has a bug with the domain name in the reset link
        # it uses api.taggedweb.com instead of the active site domain (i.e. taggedweb.com) which is why we force
        # it to use the default PasswordResetForm by overriding the all auth form
        return PasswordResetForm

    # This override only needs to be enabled if we want to customize these settings
    # def get_email_options(self):
    #     request = self.context.get('request')
    #     return {
    #         'use_https': request.is_secure(),
    #         'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
    #         ## The below line can be updated and a corresponding customize
    #         # 'email_template_name': 'example_message.txt',
    #         'request': request,
    #     }
