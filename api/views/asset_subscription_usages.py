from rest_framework import viewsets, permissions

from api.models.asset_subscription_usage import AssetSubscriptionUsage
from api.serializers.asset_subscription_usage import AssetSubscriptionUsageSerializer


class AssetSubscriptionUsagesViewSet(viewsets.ModelViewSet):
    queryset = AssetSubscriptionUsage.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = AssetSubscriptionUsageSerializer
