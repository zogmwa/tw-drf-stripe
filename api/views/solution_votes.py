from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from api.models import SolutionVote, Solution
from api.serializers.solution_vote import SolutionVoteSerializer


class SolutionVoteViewSet(viewsets.ModelViewSet):
    queryset = SolutionVote.objects.filter(is_upvote=True)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SolutionVoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'solution__id',
        'solution__slug',
    ]
    lookup_field = 'id'

    def get_queryset(self):
        if self.action == 'list':
            # /solution_votes/ (List View)
            # Returns all votes associated with the currently logged in user, filtering by solution allowed using the
            # solution__slug GET parameter. We only return currently logged in user's votes because, the aggregate vote
            # counts are already returned at the solution level and each vote instance need not be returned.
            votes = SolutionVote.objects.filter(user=self.request.user, is_upvote=True)
            return votes
        elif self.action == 'retrieve' or self.action == 'destroy':
            solution_vote_id = self.kwargs['id']
            return SolutionVote.objects.filter(
                id=solution_vote_id, user=self.request.user, is_upvote=True
            )
        else:
            super(SolutionVoteViewSet, self).get_queryset()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        solution_id = self.request.data.get('solution')
        solution = Solution.objects.get(id=solution_id)
        solution_upvote, created = SolutionVote.objects.get_or_create(
            user=user,
            solution=solution,
        )
        solution_upvote.save()
        solution_upvote_serializer = SolutionVoteSerializer(solution_upvote)
        return Response(solution_upvote_serializer.data)
