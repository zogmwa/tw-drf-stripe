from rest_framework import generics
from django.views.generic.detail import SingleObjectMixin
from rest_framework import viewsets, permissions, mixins, generics
from rest_framework.decorators import action

from api.models import User, Organization
from api.serializers.user import UserSerializer
from api.serializers.organization import OrganizationSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
