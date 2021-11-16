from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from api.views.common import extract_results_from_matching_query

from api.models import SolutionQuestion, Solution
from api.documents.solution_question import SolutionQuestionDocument
from api.serializers.solution_question import (
    SolutionQuestionSerializer,
)


class SolutionQuestionViewSet(viewsets.ModelViewSet):
    queryset = SolutionQuestion.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['solution__slug', 'submitted_by__username']

    def get_serializer_class(self):
        return SolutionQuestionSerializer


def autocomplete_solution_questions(request):
    """
    The view serves as an endpoint to autocomplete solution question titles and uses an elasticsearch index.
    """
    q = request.GET.get('q')
    solution_slug = request.GET.get('solution__slug')

    if q and len(q) >= 3:
        es_search = SolutionQuestionDocument.search().query(
            'match_phrase_prefix', title=q
        )
        results = extract_results_from_matching_query(
            es_search, case='solution_question'
        )
    else:
        results = []

    solution = Solution.objects.get(slug=solution_slug)
    solution_questions = solution.questions.filter(title__in=results)
    serializer = SolutionQuestionSerializer(solution_questions, many=True)
    return JsonResponse({'results': serializer.data})
