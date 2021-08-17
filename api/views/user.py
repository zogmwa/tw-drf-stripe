from rest_framework import viewsets, permissions

from api.models import User
from api.serializers.user import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'