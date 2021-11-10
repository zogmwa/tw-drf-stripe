from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from api.models import AssetVote, Asset, AssetAttributeVote
from api.serializers.asset_attribute_vote import AssetAttributeVoteSerializer
from api.serializers.asset_vote import AssetVoteSerializer

AssetAttributeVoteSerializer


class AssetAttributeVoteViewSet(viewsets.ModelViewSet):
    """
    Views to filter and return attribute votes i.e. votes on a specific feature/attribute of an asset.
    """

    queryset = AssetAttributeVote.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssetAttributeVoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {'asset__slug': ['exact'], 'is_upvote': ['exact']}

    def get_queryset(self):
        if self.action == 'list':
            # /api/attribute_votes/ (List View)
            # Returns all attribute votes associated with the currently logged in user, filtering by asset allowed
            # using the asset GET parameter (asset slug). We only return currently logged in user's votes because,
            # the aggregate vote counts are already returned at the attributes level. From a privacy standpoint, a user
            # should only be shown their attribute_votes
            attribute_votes = AssetAttributeVote.objects.filter(
                user=self.request.user,
            )

            return attribute_votes

        elif self.action == 'retrieve' or self.action == 'destroy':
            asset_attribute_vote_id = self.kwargs['pk']
            return AssetAttributeVote.objects.filter(id=asset_attribute_vote_id)
        else:
            super(AssetAttributeVoteViewSet, self).get_queryset()
