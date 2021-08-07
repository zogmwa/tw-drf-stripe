from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination

from api.documents import TagDocument


class ProviderViewSetPagination(PageNumberPagination):
    page_size = 50


def autocomplete_tags(request):
    """
    The view serves as an endpoint to autocomplete tags and uses an elasticsearch index.
    """
    # TODO: For now this is open but require an API key to use this endpoint as well for proper rate limiting.
    max_items = 10
    q = request.GET.get('q')
    if q and len(q) >= 3:
        es_search = TagDocument.search().query('match_phrase_prefix', name=q)
        results = []
        for i, hit in enumerate(es_search):
            if i >= max_items:
                break
            else:
                results.append(hit.slug)
    else:
        results = []

    return JsonResponse({
        'results': results
    })
