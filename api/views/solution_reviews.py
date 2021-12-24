from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from api.models import SolutionReview, Solution
from api.serializers.solution_review import SolutionReviewSerializer


class SolutionReviewViewSet(viewsets.ModelViewSet):
    queryset = SolutionReview.objects.filter()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = SolutionReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'solution__id': ['exact'],
        'user__username': ['exact'],
    }

    def create(self, request, *args, **kwargs):
        user = self.request.user
        solution_id = self.request.data.get('solution')
        review_type = self.request.data.get('type')
        try:
            solution = Solution.objects.get(id=solution_id)

            try:
                solution_review = SolutionReview.objects.get(
                    user=user,
                    solution=solution,
                )

                if solution_review.type == review_type:
                    solution_review.delete()
                    return Response(status=status.HTTP_200_OK)
                else:
                    solution_review.type = review_type
                    solution_review.save()
            except SolutionReview.DoesNotExist:
                solution_review = SolutionReview.objects.create(
                    user=user,
                    solution=solution,
                    type=review_type,
                )

            solution_review_serializer = SolutionReviewSerializer(solution_review)

            return Response(solution_review_serializer.data)
        except Solution.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
