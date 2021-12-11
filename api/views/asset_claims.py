from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import AssetClaim
from api.permissions.allow_owner_or_admin_and_staff import IsObjectOwnerOrAdminOrStaff
from api.serializers.claim_asset import (
    AssetClaimUserSerializer,
    AssetClaimSerializer,
)


class AssetClaimViewSet(viewsets.ModelViewSet):
    """
    This flow is used when a prospective Software owner submits a claim that they own a software and want to
    be able to manage it. A GET operation will only return claims that the currently logged in user has submitted
    unless the user is an admin or staff user.
    """

    queryset = AssetClaim.objects.filter()

    # Owner in the AllowOwner prefix in this case refers to the user who created the claim request (not the user who
    # owns the asset). A user who created a claim should be able do edit/modify it to change their comment.
    permission_classes = [IsObjectOwnerOrAdminOrStaff]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return AssetClaimSerializer
        return AssetClaimUserSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'status': ['exact'],
        'asset__slug': ['exact'],
        # This filter is a bit pointless because only the currently logged in user's claim requests will be returned.
        # It's useful for debugging if a staff/admin member is testing the endpoint.
        'user__username': ['exact'],
    }

    def get_queryset(self):
        claim_asset_db_queryset = super(AssetClaimViewSet, self).get_queryset()

        if self.action == 'list':
            if not self.request.user.is_staff and not self.request.user.is_superuser:
                claim_asset_db_queryset = claim_asset_db_queryset.filter(
                    user=self.request.user
                )
            return claim_asset_db_queryset

        elif self.action == 'retrieve' or self.action == 'destroy':
            asset_claim_id = self.kwargs['pk']
            # Since we only return the asset claims the user owns, they can only delete that asset claim
            return AssetClaim.objects.filter(id=asset_claim_id, user=self.request.user)
        else:
            return claim_asset_db_queryset
