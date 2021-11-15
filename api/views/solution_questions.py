from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from api.models import SolutionQuestion
from api.serializers.solution_question import (
    SolutionQuestionSerializer,
)


class SolutionQuestionViewSet(viewsets.ModelViewSet):
    queryset = SolutionQuestionSerializer.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['solution__slug', 'submitted_by__username']

    def get_serializer_class(self):
        return SolutionQuestionSerializer
