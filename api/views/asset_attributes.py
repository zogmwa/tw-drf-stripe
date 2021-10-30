from django.http import JsonResponse
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from api.documents.attribute import AttributeDocument
from api.models import Attribute
from api.serializers.asset_attribute import (
    AssetAttributeSerializer,
    AuthenticatedAssetAttributeSerializer,
)
from api.views.common import extract_results_from_matching_query


class AssetAttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assets__slug']

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return AssetAttributeSerializer
        else:
            return AuthenticatedAssetAttributeSerializer


def autocomplete_attributes(request):
    """
    (To be deprecated: Use autocomplete_assets_and_tags instead of this)
    The view serves as an endpoint to autocomplete tags and uses an elasticsearch index.
    """
    # TODO: For now this is open but require an API key to use this endpoint as well for proper rate limiting.
    q = request.GET.get('q')
    if q and len(q) >= 3:
        es_search = AttributeDocument.search().query('match_phrase_prefix', name=q)
        results = extract_results_from_matching_query(es_search, case='attribute')
    else:
        results = []

    return JsonResponse({'results': results})
