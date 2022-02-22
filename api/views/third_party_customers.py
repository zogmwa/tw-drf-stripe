from rest_framework import (
    permissions,
    viewsets,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import ThirdPartyCustomer
from api.serializers.third_party_customer import ThirdPartyCustomerSerializer
from api.views.user import UserViewSet


class ThirdPartyCustomerViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = ThirdPartyCustomer.objects.all()
    serializer_class = ThirdPartyCustomerSerializer

    @action(
        detail=False, permission_classes=[permissions.IsAuthenticated], methods=['get']
    )
    def customer_payment_method_count(self, request, *args, **kwargs):
        """
        If our partners want to know customer's payment methods count
        http://127.0.0.1:8000/third_party_customers/customer_payment_method_count/?customer_uid=<customer_uid>
        """
        user = self.request.user
        customer_uid = request.GET.get('customer_uid', '')
        try:
            third_party_customer = ThirdPartyCustomer.objects.get(
                customer_uid=customer_uid, organization=user.organization
            )
            stripe_customer = third_party_customer.stripe_customer
            if stripe_customer is None:
                return Response({'payment_methods': 0})

            return_payment_methods = UserViewSet._fetch_payment_methods(stripe_customer)
            return Response({'payment_methods': len(return_payment_methods)})
        except ThirdPartyCustomer.DoesNotExist:
            return Response(
                data={"detail": "Third party customer does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
