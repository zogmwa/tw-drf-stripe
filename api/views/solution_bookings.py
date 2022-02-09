from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.pagination import LimitOffsetPagination

from api.models.solution_booking import SolutionBooking
from api.serializers.solution_booking import (
    AuthenticatedSolutionBookingSerializer,
)


class SolutionBookingViewSetPagination(LimitOffsetPagination):
    default_limit = 5
    limit_query_param = "limit"
    offset_query_param = "offset"
    max_limit = 10


class SolutionBookingViewSet(viewsets.ModelViewSet):
    queryset = SolutionBooking.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'created': ['gte', 'lte'],
        'updated': ['gte', 'lte'],
        'status': ['exact'],
    }
    pagination_class = SolutionBookingViewSetPagination

    def get_serializer_class(self):
        return AuthenticatedSolutionBookingSerializer

    def get_queryset(self):
        if self.action == 'list':
            solution_booking_queryset = SolutionBooking.objects.filter(
                booked_by=self.request.user
            )

            return solution_booking_queryset
        elif (
            self.action == 'retrieve'
            or self.action == 'partial_update'
            or self.action == 'destroy'
        ):
            solution_booking_id = self.kwargs['pk']
            return SolutionBooking.objects.filter(id=solution_booking_id)
