from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from api.models import AssetVote, Asset
from api.serializers.asset_vote import AssetVoteSerializer


class AssetVoteViewSet(viewsets.ModelViewSet):
    queryset = AssetVote.objects.filter(is_upvote=True)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssetVoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'asset__id',
        'asset__slug',
    ]
    lookup_field = 'id'

    def get_queryset(self):
        if self.action == 'list':
            # /api/votes/ (List View)
            # Returns all votes associated with the currently logged in user, filtering by asset allowed using the
            # asset__slug GET parameter. We only return currently logged in user's votes because, the aggregate vote
            # counts are already returned at the asset level and each vote instance need not be returned.
            votes = AssetVote.objects.filter(user=self.request.user, is_upvote=True)
            return votes
        elif self.action == 'retrieve' or self.action == 'destroy':
            asset_vote_id = self.kwargs['id']
            return AssetVote.objects.filter(
                id=asset_vote_id, user=self.request.user, is_upvote=True
            )
        else:
            super(AssetVoteViewSet, self).get_queryset()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        asset_id = self.request.data.get('asset')
        asset = Asset.objects.get(id=asset_id)
        asset_upvote, created = AssetVote.objects.get_or_create(
            user=user,
            asset=asset,
        )
        asset_upvote.save()
        asset_upvote_serializer = AssetVoteSerializer(asset_upvote)
        return Response(asset_upvote_serializer.data)
