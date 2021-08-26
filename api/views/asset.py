from django.db.models import QuerySet, Count, F, Q
from elasticsearch_dsl.query import MultiMatch
from rest_framework import viewsets, permissions, generics, status
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.documents import AssetDocument
from api.models import Asset, Tag
from api.serializers.asset import AssetSerializer


class AssetViewSetPagination(LimitOffsetPagination):
    default_limit = 20
    limit_query_param = "limit"
    offset_query_param = "offset"
    max_limit = 100


class AssetViewSet(viewsets.ModelViewSet):

    queryset = Asset.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = AssetSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {'avg_rating': ['gte', 'lte']}
    ordering_fields = ['avg_rating', 'upvotes_count']
    lookup_field = 'slug'
    pagination_class = AssetViewSetPagination

    def _update_tag_search_counts_for_tags_used_in_search_query(self, search_query):
        tags = search_query.split()
        Tag.objects.filter(slug__in=tags).distinct().update(counter=F('counter') + 1)
        return

    @staticmethod
    def _filter_assets_matching_tags_exact(tag_slugs: list) -> QuerySet:
        """
        DB level AND filter to fetch only those assets that have all the given tags.
        """
        desired_tags = Tag.objects.filter(slug__in=tag_slugs).all()

        # First create a query which filters having at-least as many tags as those in the desired list
        # Then filter the assets which have each of the desired tag.
        assets = Asset.objects.annotate(c=Count('tags')).filter(
            c__gte=len(desired_tags)
        )
        for tag in desired_tags:
            assets = assets.filter(tags__in=[tag])
        return assets

    @staticmethod
    def _get_assets_db_qs_via_elasticsearch_query(search_query: str) -> QuerySet:
        """
        Given a search query string uses that to perform a MultiMatch search query against ElasticSearch indexes.
        """
        es_query = MultiMatch(
            query=search_query,
            fields=['tags.slug^2', 'short_description', 'description', 'name^3'],
            # If number of tokenized words/clauses in query is less than or equal to 3, they are all required,
            # after that this will even return results if the threshold % of the tags/clauses are present.
            minimum_should_match='3<75%',
        )
        es_search = AssetDocument.search().query(es_query)
        assets_db_queryset = es_search.to_queryset()
        assets_db_queryset = assets_db_queryset.filter(is_published=True)
        return assets_db_queryset

    def get_queryset(self):
        if self.action == 'list':
            # /api/assets/?q=<Search Keywords> (List View)
            # q is the search query containing space separated tag slugs or a product name
            search_query = self.request.query_params.get('q')

            if search_query is None:
                return Asset.objects.none()

            self._update_tag_search_counts_for_tags_used_in_search_query(search_query)

            assets_db_queryset = self._get_assets_db_qs_via_elasticsearch_query(
                search_query
            )
            return assets_db_queryset

        elif self.action == 'retrieve':
            slug = self.kwargs['slug']
            return Asset.objects.filter(slug=slug, is_published=True)
        else:
            super(AssetViewSet, self).get_queryset()

    @action(detail=False)
    def similar(self, request, *args, **kwargs):
        """
        Example(s):
        - /assets/similar/?name=mailchimp
        - /assets/similar/?name=mailchimp&include_self=1

        The resulting wil may also have the asset being searched for
        """
        asset_name_query = self.request.query_params.get('name')

        # By default the self asset is included unless a include_self=0 GET parameter is passed to exclude it
        include_self = int(self.request.query_params.get('include_self', '1'))
        if asset_name_query is None:
            return Response(
                data={"detail": "name GET containing asset name must be provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        asset = (
            Asset.objects.filter(name__istartswith=asset_name_query)
            .prefetch_related('tags')
            .get()
        )

        q = ' '.join(tag.slug for tag in asset.tags.all())
        assets_db_qs = self._get_assets_db_qs_via_elasticsearch_query(q)

        if not include_self:
            assets_db_qs = assets_db_qs.filter(~Q(id=asset.id))
        else:
            assets_db_qs = assets_db_qs | Asset.objects.filter(id=asset.id)

        page = self.paginate_queryset(assets_db_qs)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(assets_db_qs, many=True)
        return Response(serializer.data)
