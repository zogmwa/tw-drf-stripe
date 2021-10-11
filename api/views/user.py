from rest_framework import viewsets
from api.models import User
from api.serializers.user import UserSerializer
from api.permissions.user_permissions import AllowOwnerOrAdminOrStaff


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    permission_classes = [AllowOwnerOrAdminOrStaff]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
