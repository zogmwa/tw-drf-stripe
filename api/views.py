from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q, Count, QuerySet
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
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
    lookup_field = 'name'

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
            tag_slugs = tags.strip().split(',')
            filtered_assets = self._filter_assets_matching_tags(tag_slugs)
            return filtered_assets

        elif self.action == 'retrieve':
            # TODO
            pass
        else:
            super(AssetViewSet, self).get_queryset()
