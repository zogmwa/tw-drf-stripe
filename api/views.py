from django.db.models import Count, QuerySet
from django.http import JsonResponse
from elasticsearch_dsl.query import MultiMatch, Nested, Q as ESQ, Match
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from api.documents import TagDocument, AssetDocument
from api.models import Asset, Tag, AssetQuestion
from api.serializers import AssetSerializer, AssetQuestionSerializer


class ProviderViewSetPagination(PageNumberPagination):
    page_size = 50


################# Views ##################
##########################################


class AssetViewSet(viewsets.ModelViewSet):

    queryset = Asset.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = AssetSerializer
    lookup_field = 'slug'

    @staticmethod
    def _filter_assets_matching_tags_exact(tag_slugs: list) -> QuerySet:
        """
        DB level AND filter to fetch only those assets that have all the given tags.
        """
        desired_tags = Tag.objects.filter(slug__in=tag_slugs).all()

        # First create a query which filters having at-least as many tags as those in the desired list
        # Then filter the assets which have each of the desired tag.
        assets = Asset.objects.annotate(c=Count('tags')).filter(c__gte=len(desired_tags))
        for tag in desired_tags:
            assets = assets.filter(tags__in=[tag])
        return assets

    def get_queryset(self):
        if self.action == 'list':
            # /api/assets/?q=<Search Keywords> (List View)
            # Eventually deprecate tags query and move to q, since q can be any keywords including asset name
            # not just tags.
            search_query = self.request.query_params.get('tags') or self.request.query_params.get('q')

            if search_query is None:
                # If no tags are provided return nothing, no more returning of default sample
                return []

            es_query = MultiMatch(
                query=search_query,
                fields=['tags.slug^2', 'description', 'name^3'],
                # If number of tokenized words/clauses in query is less than or equal to 3, they are all required,
                # after that this will even return results if the threshold % of the tags/clauses are present.
                minimum_should_match='3<75%',
            )

            es_search = AssetDocument.search().query(es_query)
            assets_db_queryset = es_search.to_queryset()
            # assets_db_queryset = self._filter_assets_matching_tags_exact(tag_slugs)
            return assets_db_queryset

        elif self.action == 'retrieve':
            slug = self.kwargs['slug']
            return Asset.objects.filter(slug=slug)
        else:
            super(AssetViewSet, self).get_queryset()


class AssetQuestionViewSet(viewsets.ModelViewSet):
    queryset = AssetQuestion.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = AssetQuestionSerializer

    def get_queryset(self):
        if self.action == 'list':
            # /api/questions/ (List View)
            asset_slug = self.request.query_params.get('asset')

            if asset_slug is None:
                return []

            asset_slug = asset_slug.strip()
            filtered_questions = AssetQuestion.objects.filter(asset__slug=asset_slug)
            return filtered_questions
        else:
            super(AssetQuestionViewSet, self).get_queryset()


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
