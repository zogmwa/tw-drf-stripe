from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status

from api.documents.solution import SolutionDocument
from api.models.solution import Solution
from api.serializers.solution import SolutionSerializer
from api.views.common import extract_results_from_matching_query


class SolutionViewSet(viewsets.ModelViewSet):

    queryset = Solution.objects.filter()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'title',
    ]
    serializer_class = SolutionSerializer


def autocomplete_solutions(request):
    """
    The view serves as an endpoint to autocomplete solution titles and uses an elasticsearch index.
    """
    # TODO: For now this is open but require an API key to use this endpoint as well for proper rate limiting.
    q = request.GET.get('q')
    if q and len(q) >= 3:
        es_search = SolutionDocument.search().query('match_phrase_prefix', title=q)
        results = extract_results_from_matching_query(es_search, case='solution')
    else:
        results = []

    return JsonResponse({'results': results})
