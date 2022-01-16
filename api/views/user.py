import stripe
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from djstripe.models import Customer as StripeCustomer
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

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['post'])
    def attach_card(self, request, *args, **kwargs):
        if request.data.get('payment_method'):
            user = self.request.user
            if user.first_name is None and user.last_name is None:
                username = user.username
            else:
                username = '{} {}'.format(user.first_name, user.last_name)
            # Create user's customer
            stripe_customer = stripe.Customer.create(email=user.email, name=username)
            djstripe_customer = StripeCustomer.sync_from_stripe_data(stripe_customer)
            user.stripe_customer = djstripe_customer
            user.save()
            # Attact payment method to customer
            stripe_payment_method = stripe.PaymentMethod.attach(
                request.data.get('payment_method'), customer=stripe_customer.id
            )
            stripe_customer_with_payment_method = stripe.Customer.modify(
                stripe_customer.id,
                invoice_settings={
                    'default_payment_method': stripe_payment_method.id,
                },
            )
            StripeCustomer.sync_from_stripe_data(stripe_customer_with_payment_method)
            return Response(stripe_customer_with_payment_method)
        else:
            return Response(
                data={"detail": "incorrect payment method"},
                status=status.HTTP_400_BAD_REQUEST,
            )
