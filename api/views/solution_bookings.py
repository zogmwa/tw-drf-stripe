from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.solution import Solution
from api.models.solution_booking import SolutionBooking
from api.serializers.solution_booking import (
    SolutionBookingSerializer,
    AuthenticatedSolutionBookingSerializer,
)


class SolutionBookingViewSet(viewsets.ModelViewSet):
    queryset = SolutionBooking.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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
            return AuthenticatedSolutionBookingSerializer

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

        elif self.action == 'retrieve' or self.action == 'destroy':
            contract_id = self.kwargs['pk']
            return SolutionBooking.objects.filter(id=contract_id)
        else:
            return super().get_queryset()

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['patch'])
    def checkout_contract(self, request, *args, **kwargs):
        solution_slug = request.data.get('solution')
        stripe_session_id = request.data.get('stripe_session_id')
        try:
            contract_instance = SolutionBooking.objects.get(
                solution=Solution.objects.get(slug=solution_slug),
                stripe_session_id=stripe_session_id,
                booked_by=self.request.user,
                status=SolutionBooking.Status.CANCELLED,
            )

            SolutionBooking.objects.filter(id=contract_instance.pk).update(
                status=SolutionBooking.Status.PENDING
            )

            contract_serializer = AuthenticatedSolutionBookingSerializer(
                SolutionBooking.objects.get(id=contract_instance.pk),
                context={'request': request},
            )

            return Response(contract_serializer.data)
        except SolutionBooking.DoesNotExist:
            return Response(status=status.HTTP_409_CONFLICT)
