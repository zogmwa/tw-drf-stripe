from django.http import JsonResponse

from api.documents.organization import OrganizationDocument
from api.views.common import extract_results_from_matching_query


def autocomplete_organizations(request):
    # TODO: For now this is open but require an API key to use this endpoint as well for proper rate limiting.
    q = request.GET.get('q')
    if q and len(q) >= 2:
        es_search = OrganizationDocument.search().query('match_phrase_prefix', name=q)
        results = extract_results_from_matching_query(es_search, case='organization')
    else:
        results = []

    return JsonResponse({'results': results})
