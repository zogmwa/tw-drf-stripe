from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from api.models import Asset, ClaimAsset
from api.serializers.claim_asset import (
    ClaimAssetUserSerializer,
    ClaimAssetAdminSerializer,
)
from api.permissions.allow_owner_or_admin_and_staff import AllowOwnerOrAdminOrStaff

from dj_rest_auth.views import LogoutView


class LogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        result = super(LogoutView, self).get(request)
        request.user.auth_token.delete()
        return result


class ClaimAssetViewSet(viewsets.ModelViewSet):
    queryset = ClaimAsset.objects.filter()
    permission_classes = [AllowOwnerOrAdminOrStaff]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ClaimAssetAdminSerializer
        return ClaimAssetUserSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'status': ['exact'],
        'asset__slug': ['exact'],
        'user__username': ['exact'],
    }

    def get_queryset(self):
        claim_asset_db_queryset = super(ClaimAssetViewSet, self).get_queryset()

        if self.action == 'list':
            if not self.request.user.is_staff and not self.request.user.is_superuser:
                claim_asset_db_queryset = claim_asset_db_queryset.filter(
                    user=self.request.user
                )
        return claim_asset_db_queryset

    def destroy(self, request, *args, **kwargs):
        instance = ClaimAsset.objects.get(id=self.kwargs['pk'])

        try:
            # Only the user who owns the review should be able to delete it
            if instance.user.id == self.request.user.id:
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_304_NOT_MODIFIED)
        except Http404:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)
