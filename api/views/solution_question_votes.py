from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from api.models import SolutionQuestionVote
from api.serializers.solution_question_vote import SolutionQuestionVoteSerializer


class SolutionQuestionVoteViewSet(viewsets.ModelViewSet):
    """
    Views to return votes on questions added by logged in user.
    Requries the user to be logged in an a question__solution__slug should be provided in the url parameters.
    """

    queryset = SolutionQuestionVote.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SolutionQuestionVoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question__solution__slug', 'question__title']

    def get_queryset(self):
        if self.action == 'list':
            # /api/question_votes/ (List View)

            return SolutionQuestionVote.objects.filter(
                is_upvote=True,
                user=self.request.user,
            )

        elif self.action == 'retrieve' or self.action == 'destroy':
            solution_question_vote_id = self.kwargs['pk']
            return SolutionQuestionVote.objects.filter(
                id=solution_question_vote_id, is_upvote=True
            )
        else:
            super(SolutionQuestionVoteViewSet, self).get_queryset()
