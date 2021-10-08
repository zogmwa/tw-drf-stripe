from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from api.models import Attribute
from api.serializers.asset_attribute import (
    AssetAttributeSerializer,
    AuthenticatedAssetAttributeSerializer,
)


class AssetAttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assets__slug']

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return AssetAttributeSerializer
        else:
            return AuthenticatedAssetAttributeSerializer
