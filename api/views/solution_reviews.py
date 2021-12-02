from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.models import SolutionReview
from api.permissions.allow_anonymous_reads_and_owner_writes import (
    AllowAnonymousReadsAndOwnerOrAdminWrites,
)
from api.serializers.solution_review import SolutionReviewSerializer


class SolutionReviewViewSet(viewsets.ModelViewSet):
    queryset = SolutionReview.objects.filter()
    permission_classes = [AllowAnonymousReadsAndOwnerOrAdminWrites]
    serializer_class = SolutionReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'rating': ['gte', 'lte'],
        'solution__slug': ['exact'],
        'user__username': ['exact'],
    }
    # create/update methods for this are overriden at serializer level

    def destroy(self, request, *args, **kwargs):
        instance = SolutionReview.objects.get(id=self.kwargs['pk'])

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
