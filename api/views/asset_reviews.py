from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from api.models import Asset, AssetReview
from api.serializers.asset_review import AssetReviewSerializer


class AssetReviewViewSet(viewsets.ModelViewSet):
    queryset = AssetReview.objects.filter()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = AssetReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'rating': ['gte', 'lte'],
        'asset__slug': ['exact'],
        'user__username': ['exact'],
    }
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
