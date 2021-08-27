from django.http import JsonResponse

from api.documents.asset import AssetDocument
from api.documents.tag import TagDocument
from api.views.common import extract_results_from_matching_query


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
            'tags': extract_results_from_matching_query(es_search_tags, case='tag'),
            'assets': extract_results_from_matching_query(
                es_search_assets, case='asset'
            ),
        }
    else:
        results_dict = {'tag_slugs': [], 'asset_names': []}

    return JsonResponse(results_dict)
