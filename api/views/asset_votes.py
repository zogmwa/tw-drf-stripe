from django.http import Http404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from api.models import AssetVote, Asset
from api.serializers.asset_vote import AssetVoteSerializer


class AssetVoteViewSet(viewsets.ModelViewSet):
    queryset = AssetVote.objects.filter(is_upvote=True)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssetVoteSerializer

    def get_queryset(self):
        if self.action == 'list':
            # /api/votes/ (List View)
            # Returns all votes associated with the currently logged in user, filtering by asset allowed using the
            # asset GET parameter. We only return currently logged in user's votes because, the aggregate vote
            # counts are already returned at the asset level and each vote instance need not be returned.

            asset_slug = self.request.query_params.get('asset', '')
            asset_slug = asset_slug.strip()

            votes = AssetVote.objects.filter(user=self.request.user, is_upvote=True)

            if asset_slug:
                votes = votes.filter(asset__slug__iexact=asset_slug)

            return votes
        elif self.action == 'retrieve':
            asset_vote_id = self.kwargs['pk']
            return AssetVote.objects.filter(id=asset_vote_id, is_upvote=True)
        else:
            super(AssetVoteViewSet, self).get_queryset()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        asset = Asset.objects.get(id=self.request.data.get('asset'))
        asset_upvote, created = AssetVote.objects.get_or_create(
            user=user,
            asset=asset,
        )
        asset_upvote.save()
        asset_upvote_serializer = AssetVoteSerializer(asset_upvote)
        return Response(asset_upvote_serializer.data)

    def destroy(self, request, *args, **kwargs):
        asset_slug = self.request.data.get('asset', '')
        asset_slug.strip()
        if not asset_slug:
            return Response(
                data={"detail": "asset parameter containing asset_id was not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            asset = Asset.objects.get(slug=asset_slug)

        instance = AssetVote.objects.get(id=self.kwargs['pk'], is_upvote=True)

        try:
            asset = AssetVote.objects.get(
                is_upvote=True,
                user=self.request.user,
                asset=asset,
            )
            if instance.user.id == self.request.user.id:
                # Only allow the user to delete the resource if it belongs to them
                self.perform_destroy(asset)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_304_NOT_MODIFIED)
        except Http404:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)
