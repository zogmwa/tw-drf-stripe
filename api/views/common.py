from django.http import JsonResponse
from django_elasticsearch_dsl.search import Search
from rest_framework.pagination import PageNumberPagination

from api.documents import TagDocument, AssetDocument


class ProviderViewSetPagination(PageNumberPagination):
    page_size = 50


def _extract_results_from_matching_query(es_search: Search, case='tag') -> list:
    """From a matching es_search_query extract relevant results"""
    results = set()
    max_unique_items = 7

    # In the rare case of deleting and re-adding objects, there can be a scenario where the same item occurs
    # more than once in the index, we want to ensure response has unique results.
    max_processed_items = 10
    for i, hit in enumerate(es_search):
        if len(results) > max_unique_items or i >= max_processed_items:
            break
        else:
            # We are using the tag slug for suggestions for tags and name for assets
            if case == 'tag':
                results.add(hit.slug)
            else:
                results.add(hit.name)
    return list(results)


def autocomplete_tags(request):
    """
    (To be deprecated: Use autocomplete_assets_and_tags instead of this)
    The view serves as an endpoint to autocomplete tags and uses an elasticsearch index.
    """
    # TODO: For now this is open but require an API key to use this endpoint as well for proper rate limiting.
    q = request.GET.get('q')
    if q and len(q) >= 3:
        es_search = TagDocument.search().query('match_phrase_prefix', name=q)
        results = _extract_results_from_matching_query(es_search)
    else:
        results = []

    return JsonResponse({'results': results})


def autocomplete_assets_and_tags(request):
    """
    The view serves as an endpoint to autocomplete asset names and tags and uses an elasticsearch index.
    """
    q = request.GET.get('q')
    if q and len(q) >= 2:
        es_search_tags = TagDocument.search().query('match_phrase_prefix', name=q)
        es_search_assets = AssetDocument.search().query('match_phrase_prefix', name=q)
        results_dict = {
            'tags': _extract_results_from_matching_query(es_search_tags, case='tag'),
            'assets': _extract_results_from_matching_query(
                es_search_assets, case='asset'
            ),
        }
    else:
        results_dict = {'tag_slugs': [], 'asset_names': []}

    return JsonResponse(results_dict)
