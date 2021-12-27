from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from api.models import SolutionReview
from api.serializers.solution_review import SolutionReviewSerializer


class SolutionReviewViewSet(viewsets.ModelViewSet):
    queryset = SolutionReview.objects.filter()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = SolutionReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'solution__id': ['exact'],
        'user__username': ['exact'],
    }
