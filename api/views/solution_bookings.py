from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from api.models.solution import SolutionBooking
from api.serializers.solution_booking import SolutionBookingSerializer


class SolutionBookingViewSet(viewsets.ModelViewSet):

    queryset = SolutionBooking.objects.filter()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'created': ['gte', 'lte'],
        'updated': ['gte', 'lte'],
        'status': ['exact'],
    }
    serializer_class = SolutionBookingSerializer
