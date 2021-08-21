from rest_framework import viewsets, permissions

from api.models import AssetQuestion
from api.serializers.asset_question import AssetQuestionSerializer


class AssetQuestionViewSet(viewsets.ModelViewSet):
    queryset = AssetQuestion.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = AssetQuestionSerializer

    def get_queryset(self):
        if self.action == 'list':
            # /api/questions/ (List View)
            asset_slug = self.request.query_params.get('asset')

            if asset_slug is None:
                return []

            asset_slug = asset_slug.strip()
            filtered_questions = AssetQuestion.objects.filter(asset__slug=asset_slug)
            return filtered_questions
        else:
            super(AssetQuestionViewSet, self).get_queryset()
