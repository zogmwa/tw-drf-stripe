from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.documents.asset import AssetDocument
from api.documents.tag import TagDocument
from api.views.common import extract_results_from_matching_query
from api.models import Tag
from api.serializers.tag import TagSerializer, TopTagSerializer


def autocomplete_tags(request):
    """
    (To be deprecated: Use autocomplete_assets_and_tags instead of this)
    The view serves as an endpoint to autocomplete tags and uses an elasticsearch index.
    """
    # TODO: For now this is open but require an API key to use this endpoint as well for proper rate limiting.
    q = request.GET.get('q')
    if q and len(q) >= 3:
        es_search = TagDocument.search().query('match_phrase_prefix', name=q)
        results = extract_results_from_matching_query(es_search)
    else:
        results = []

    tags = Tag.objects.filter(slug__in=results)
    tag_serializer = TagSerializer(tags, many=True)

    return JsonResponse({'results': tag_serializer.data})


def autocomplete_assets_and_tags(request):
    """
    The view serves as an endpoint to autocomplete asset names and tags and uses an elasticsearch index.
    """
    q = request.GET.get('q')
    tags_key = 'tags'
    asset_names_key = 'assets'
    asset_slugs_key = 'asset_slugs'

    # asset_names and asset_slugs will have a 1:1 pairity, not passing them as a combined dict for backwards
    # compatibility with frontend (as the frontend is already conssume asset names from 'assets' key right now)
    results_dict = {tags_key: [], asset_names_key: [], asset_slugs_key: []}

    if q and len(q) >= 2:
        es_search_tags = TagDocument.search().query('match_phrase_prefix', name=q)
        es_search_assets = AssetDocument.search().query('match_phrase_prefix', name=q)
        results_dict[tags_key] = extract_results_from_matching_query(
            es_search_tags, case='tag'
        )
        asset_results = extract_results_from_matching_query(
            es_search_assets, case='asset_name_and_slug'
        )  # type: list[tuple]
        # asset_results contains something like [(asset1_name, asset1_slug), ...]
        if len(asset_results) > 0:
            asset_names, asset_slugs = zip(*asset_results)
        else:
            asset_names, asset_slugs = [], []
        results_dict[asset_names_key] = asset_names
        results_dict[asset_slugs_key] = asset_slugs

    # The frontend should know that the assets and asset_slugs in the response have 1:1 pairity
    # i.e. for the same index the name and the slug point to the same asset
    return JsonResponse(results_dict)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = TagSerializer
    tags_slug_list = [
        'accounting',
        'analytics',
        'vpn',
        'compliance',
        'crm',
        'email-marketing',
        'e-commerce',
        'erp',
        'environmental-compliance',
        'artificial-intelligence',
        'marketplace',
        'marketing-automation',
    ]

    @action(
        detail=False,
        permission_classes=[IsAuthenticatedOrReadOnly],
        methods=['get'],
        serializer_class=TopTagSerializer,
    )
    def top_tags(self, request, *args, **kwargs):
        top_tags = Tag.objects.filter(slug__in=self.tags_slug_list).values(
            'name', 'slug'
        )
        serializer = TopTagSerializer(top_tags, many=True)
        return JsonResponse({'data': serializer.data})
