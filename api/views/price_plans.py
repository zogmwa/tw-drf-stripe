from rest_framework import viewsets, permissions

from api.models import PricePlan
from api.serializers.price_plan import PricePlanSerializer


class PricePlanViewSet(viewsets.ModelViewSet):
    queryset = PricePlan.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PricePlanSerializer

    def get_queryset(self):
        if self.action == 'list':
            # /api/price_plans/ (List View)
            asset_slug = self.request.query_params.get('asset')

            if asset_slug is None:
                return []

            asset_slug = asset_slug.strip()
            filtered_price_plans = PricePlan.objects.filter(asset__slug=asset_slug)
            return filtered_price_plans
        else:
            super(PricePlanViewSet, self).get_queryset()