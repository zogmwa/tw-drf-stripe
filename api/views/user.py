from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import User
from api.models.solution_booking import SolutionBooking
from api.serializers.user import UserSerializer
from api.serializers.solution_booking import AuthenticatedSolutionBookingSerializer
from api.permissions.user_permissions import AllowOwnerOrAdminOrStaff


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    permission_classes = [AllowOwnerOrAdminOrStaff]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    @action(detail=True, permission_classes=[IsAuthenticated], methods=['get'])
    def bookings(self, request, *args, **kwargs):
        """
        If the user wants to get solution bookings list:
        http://127.0.0.1:8000/users/<username>/bookings/
        http://127.0.0.1:8000/users/<username>/bookings/?id=<solution_booking_id>
        """
        contract_id = request.GET.get('id', '')
        context_serializer = {'request': request}
        if contract_id:
            solution_booking_queryset = SolutionBooking.objects.filter(
                booked_by__username=kwargs['username'], id=contract_id
            )
        else:
            solution_booking_queryset = SolutionBooking.objects.filter(
                booked_by__username=kwargs['username']
            )

        solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
            solution_booking_queryset, context=context_serializer, many=True
        )

        return Response(solution_booking_serializer.data)
