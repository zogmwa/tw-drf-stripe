from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from elasticsearch_dsl.query import MultiMatch
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import QuerySet, Count, F, Q

from api.documents.solution import SolutionDocument
from api.models.solution import Solution
from api.serializers.solution import SolutionSerializer
from api.views.common import extract_results_from_matching_query
from api.documents.asset import AssetDocument
from api.serializers.asset import AssetSerializer, AuthenticatedAssetSerializer


class SolutionViewSet(viewsets.ModelViewSet):

    queryset = Solution.objects.filter()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'title',
    ]
    lookup_field = 'slug'
    serializer_class = SolutionSerializer

    @staticmethod
    def _get_assets_db_qs_via_elasticsearch_query(search_query: str) -> QuerySet:
        """
        Given a search query string uses that to perform a MultiMatch search query against ElasticSearch indexes.
        """
        es_query = MultiMatch(
            query=search_query,
            fields=['tags.slug', 'short_description', 'description', 'name'],
            # If number of tokenized words/clauses in query is less than or equal to 3, they are all required,
            # after that this will even return results if the threshold % of the tags/clauses are present.
        )
        es_search = AssetDocument.search().query(es_query)
        assets_db_queryset = es_search.to_queryset()
        return assets_db_queryset

    @action(detail=False)
    def related_assets(self, request, *args, **kwargs):
        """
        Returns services that are similar to a given solution.

        Example:
        - /solutions/related_assets/?slug=<solution_slug>
        """
        # Either the slug or the name parameter must be used but not both
        solution_slug_param = self.request.query_params.get('slug')

        if solution_slug_param is None:
            return Response(
                data={
                    "detail": "slug GET parameter pointing to the solution must be provided"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        solution = (
            Solution.objects.filter(slug=solution_slug_param.strip())
            .prefetch_related('tags')
            .get()
        )
        solution_tags = set()
        solution_tags.add(solution.primary_tag)
        for solution_tag in solution.tags.all():
            solution_tags.add(solution_tag)

        q = ' '.join(tag.slug for tag in solution_tags)
        assets_db_qs = self._get_assets_db_qs_via_elasticsearch_query(q)

        page = self.paginate_queryset(assets_db_qs)

        if page is not None:
            if self.request.user.is_anonymous:
                serializer = AssetSerializer(assets_db_qs, many=True)
            else:
                serializer = AuthenticatedAssetSerializer(assets_db_qs, many=True)
            return self.get_paginated_response(serializer.data)

        if self.request.user.is_anonymous:
            serializer = AssetSerializer(
                assets_db_qs,
                many=True,
                context={'request': request},
            )
        else:
            serializer = AuthenticatedAssetSerializer(
                assets_db_qs, many=True, context={'request': request}
            )

        return Response(serializer.data)

    def get_queryset(self):
        if self.action == 'list':
            solutions = Solution.objects.all()
            return solutions
        elif self.action == 'retrieve':
            slug = self.kwargs['slug']
            solution = Solution.objects.filter(slug=slug)
            return solution
        # if self.action == 'update' or something else
        else:
            super().get_queryset()


def autocomplete_solutions(request):
    """
    The view serves as an endpoint to autocomplete solution titles and uses an elasticsearch index.
    """
    q = request.GET.getlist('q')
    search_query = ' '.join(q)
    es_query = MultiMatch(
        query=search_query,
        fields=['title', 'tags.slug']
        # If number of tokenized words/clauses in query is less than or equal to 3, they are all required,
    )
    es_search = SolutionDocument.search().query(es_query)
    solutions_db_queryset = es_search.to_queryset()

    serializer = SolutionSerializer(solutions_db_queryset, many=True)
    results = serializer.data

    return JsonResponse({'results': results})
