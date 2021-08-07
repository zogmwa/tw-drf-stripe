from rest_framework import viewsets, permissions

from api.models import Attribute
from api.serializers import AssetAttributeSerializer


class AssetAttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssetAttributeSerializer
