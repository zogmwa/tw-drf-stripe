from django.db.models import QuerySet, Count
from elasticsearch_dsl.query import MultiMatch
from rest_framework import viewsets, permissions

from api.documents import AssetDocument
from api.models import Asset, Tag
from api.serializers.asset import AssetSerializer


class AssetViewSet(viewsets.ModelViewSet):

    DEFAULT_SEARCH_RESULTS_COUNT = 20
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

            # A max of num_results_per_page results will be returned
            num_results_per_page = min(
                int(self.request.query_params.get('n', self.DEFAULT_SEARCH_RESULTS_COUNT)),
                # No more than 100 results should be returned regardless of n, to protect from API query load
                100,
            )
            page = int(self.request.query_params.get('p', 0))

            if search_query is None:
                # If no tags are provided return nothing, no more returning of default sample
                return []

            es_query = MultiMatch(
                query=search_query,
                fields=['tags.slug^2', 'short_description', 'description', 'name^3'],
                # If number of tokenized words/clauses in query is less than or equal to 3, they are all required,
                # after that this will even return results if the threshold % of the tags/clauses are present.
                minimum_should_match='3<75%',
            )

            es_search = AssetDocument.search().query(es_query)
            start_page = page * num_results_per_page
            es_search = es_search[start_page:start_page+num_results_per_page]
            assets_db_queryset = es_search.to_queryset()
            assets_db_queryset = assets_db_queryset.filter(is_published=True)
            return assets_db_queryset

        elif self.action == 'retrieve':
            slug = self.kwargs['slug']
            return Asset.objects.filter(slug=slug, is_published=True)
        else:
            super(AssetViewSet, self).get_queryset()
