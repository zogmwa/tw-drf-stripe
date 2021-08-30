from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from api.models import AssetQuestionVote
from api.serializers.asset_question_vote import AssetQuestionVoteSerializer


class AssetQuestionVoteViewSet(viewsets.ModelViewSet):
    """
    Views to return votes on questions added by logged in user.
    Requries the user to be logged in an a question__asset__slug should be provided in the url parameters.
    """

    queryset = AssetQuestionVote.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssetQuestionVoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question__asset__slug', 'question__title']

    def get_queryset(self):
        if self.action == 'list':
            # /api/question_votes/ (List View)

            return AssetQuestionVote.objects.filter(
                is_upvote=True,
                user=self.request.user,
            )

        elif self.action == 'retrieve':
            asset_question_vote_id = self.kwargs['pk']
            return AssetQuestionVote.objects.filter(
                id=asset_question_vote_id, is_upvote=True
            )
        else:
            super(AssetQuestionVoteViewSet, self).get_queryset()
