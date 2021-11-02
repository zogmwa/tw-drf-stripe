from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status

from api.models.solution import Solution
from api.serializers.solution import SolutionSerializer


class SolutionViewSet(viewsets.ModelViewSet):

    queryset = Solution.objects.filter()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'title',
    ]
    serializer_class = SolutionSerializer
