from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from api.models.solution_booking import SolutionBooking
from api.serializers.solution_booking import (
    SolutionBookingSerializer,
    AuthenticatedSolutionBookingSerializer,
)


class SolutionBookingViewSet(viewsets.ModelViewSet):

    queryset = SolutionBooking.objects.filter()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'created': ['gte', 'lte'],
        'updated': ['gte', 'lte'],
        'status': ['exact'],
    }

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return SolutionBookingSerializer
        else:
            request = self.context.get('request')
            serialize_context = {'request': request}
            return AuthenticatedSolutionBookingSerializer(context=serialize_context)

    def get_queryset(self):
        if self.action == 'list':
            if self.request.user.is_anonymous:
                solution_booking_queryset = SolutionBooking.objects.all()

                return solution_booking_queryset
            else:
                solution_booking_queryset = SolutionBooking.objects.filter(
                    booked_by=self.request.user
                )

                return solution_booking_queryset
