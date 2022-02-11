from rest_framework import (
    permissions,
    viewsets,
)

from api.models import ThirdPartyCustomer
from api.serializers.third_pary_customer import ThirdPartyCustomerSerializer


class ThirdPartyCustomerViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = ThirdPartyCustomer.objects.all()
    serializer_class = ThirdPartyCustomerSerializer
