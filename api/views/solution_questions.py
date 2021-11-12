from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from api.models import SolutionQuestion
from api.serializers.solution_question import (
    SolutionQuestionSerializer,
    AuthenticatedSolutionQuestionSerializer,
)


class SolutionQuestionViewSet(viewsets.ModelViewSet):
    queryset = SolutionQuestionSerializer.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['solution__slug', 'submitted_by__username']

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return SolutionQuestionSerializer
        else:
            return AuthenticatedSolutionQuestionSerializer
