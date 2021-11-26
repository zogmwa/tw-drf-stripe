from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import QuerySet, Count, F, Q

from api.models.solution_bookmark import SolutionBookmark
from api.models.solution import Solution
from api.serializers.solution_bookmark import SolutionBookmarkSerializer


class SolutionBookmarkViewSet(viewsets.ModelViewSet):
    queryset = SolutionBookmark.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return SolutionBookmarkSerializer

    def get_queryset(self):
        if self.action == 'list':
            # /solution_bookmarks/ (List View)
            # Returns all bookmarks associated with the currently logged in user, filtering by solution allowed
            # using the solution__id GET parameter. We only return currently logged in user's bookmarks because,
            # other users bookmark solutions list is not necessary to others
            bookmarks = SolutionBookmark.objects.filter(user=self.request.user)
            return bookmarks
        elif self.action == 'retrieve' or self.action == 'destroy':
            solution_bookmark_id = self.kwargs['pk']
            return SolutionBookmark.objects.filter(
                pk=solution_bookmark_id, user=self.request.user
            )
        else:
            super(SolutionBookmarkViewSet, self).get_queryset()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        solution_id = self.request.data.get('solution')
        solution = Solution.objects.get(id=solution_id)
        solution_bookmark, created = SolutionBookmark.objects.get_or_create(
            user=user,
            solution=solution,
        )
        solution_bookmark.save()
        solution_bookmark_serializer = SolutionBookmarkSerializer(
            solution_bookmark, context={'request': request}
        )
        return Response(solution_bookmark_serializer.data)
