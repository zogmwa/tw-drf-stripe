from django.db.models import Count, QuerySet
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from api.models import Asset, Tag
from api.serializers import AssetSerializer


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
    def _filter_assets_matching_tags(tag_slugs: list) -> QuerySet:
        """
        Only those assets that have all the provided tags should be filtered. An asset can have extra tags but
        it should be filtered only if it has atleast the tags provided in the above tag_slugs list.
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
            # /api/assets/ (List View)
            tags = self.request.query_params.get('tags')

            if tags is None:
                # TODO: For now returning upto 10 assets but later we want to return nothing if no tags are provided
                return Asset.objects.all()[:10]

            tag_slugs = tags.strip().split(',')
            filtered_assets = self._filter_assets_matching_tags(tag_slugs)
            return filtered_assets

        elif self.action == 'retrieve':
            slug = self.kwargs['slug']
            return Asset.objects.filter(slug=slug)
        else:
            super(AssetViewSet, self).get_queryset()
