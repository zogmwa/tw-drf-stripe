from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from api.models import Asset, AssetReview
from api.serializers.asset_review import AssetReviewSerializer


class AssetReviewViewSet(viewsets.ModelViewSet):
    queryset = AssetReview.objects.filter()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssetReviewSerializer
    filter_backends = [DjangoFilterBackend]

    # TODO: https://github.com/taggedweb/taggedweb/issues/113 (Figure out how to do gte/lte filtering on rating)
    filterset_fields = ['asset__slug', 'user__username', 'rating']
    # create/update methods for this are overriden at serializer level

    def destroy(self, request, *args, **kwargs):
        instance = AssetReview.objects.get(id=self.kwargs['pk'])

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
