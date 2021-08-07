from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from api.models import Asset


class AssetClickThroughCounterRedirectView(RedirectView):

    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        asset = get_object_or_404(Asset, slug=kwargs['slug'])
        asset.update_clickthrough_counter()
        return asset.affiliate_link or asset.website
