from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from api.models import AssetQuestion
from api.serializers.asset_question import (
    AssetQuestionSerializer,
    AuthenticatedAssetQuestionSerializer,
)


class AssetQuestionViewSet(viewsets.ModelViewSet):
    queryset = AssetQuestion.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['asset__slug', 'submitted_by__username']

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return AssetQuestionSerializer
        else:
            return AuthenticatedAssetQuestionSerializer
