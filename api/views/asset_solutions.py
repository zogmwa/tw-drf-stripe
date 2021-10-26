from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status

from api.models.asset_solution import AssetSolution
from api.serializers.asset_solution import AssetSolutionSerializer


class AssetSolutionViewSet(viewsets.ModelViewSet):

    queryset = AssetSolution.objects.filter()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'title',
        'asset__slug',
    ]
    serializer_class = AssetSolutionSerializer
