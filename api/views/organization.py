from django.http import JsonResponse
from rest_framework import viewsets, permissions

from api.documents.organization import OrganizationDocument
from api.views.common import extract_results_from_matching_query
from api.models.organization import Organization
from api.serializers.organization import OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = 'name'


def autocomplete_organizations(request):
    # TODO: For now this is open but require an API key to use this endpoint as well for proper rate limiting.
    q = request.GET.get('q')
    if q and len(q) >= 2:
        es_search = OrganizationDocument.search().query('match_phrase_prefix', name=q)
        results = extract_results_from_matching_query(es_search, case='organization')
    else:
        results = []

    organizations = Organization.objects.filter(name__in=results)
    organization_serializer = OrganizationSerializer(organizations, many=True)
    return JsonResponse({'results': organization_serializer.data})
