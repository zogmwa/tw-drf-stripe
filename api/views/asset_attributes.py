from rest_framework import viewsets, permissions

from api.models import Attribute
from api.serializers.asset_attribute import (
    AssetAttributeSerializer,
    AuthenticatedAssetAttributeSerializer,
)


class AssetAttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return AssetAttributeSerializer
        else:
            return AuthenticatedAssetAttributeSerializer
