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
