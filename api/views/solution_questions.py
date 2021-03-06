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


def _get_solution_questions_db_qs_via_elasticsearch_query(q):
    return SolutionQuestionDocument.search().query('match_phrase_prefix', title=q)


def autocomplete_solution_questions(request):
    """
    The view serves as an endpoint to autocomplete solution question titles and uses an elasticsearch index.
    """
    q = request.GET.get('q')
    solution_slug = request.GET.get('solution__slug')
    solution = Solution.objects.get(slug=solution_slug)

    if q and len(q) >= 3:
        es_search = _get_solution_questions_db_qs_via_elasticsearch_query(q)
        results = extract_results_from_matching_query(
            es_search, case='solution_question'
        )

        solution_questions = solution.questions.filter(title__in=results)
        serializer = SolutionQuestionSerializer(solution_questions, many=True)
    else:
        if q == '':
            solution_questions = solution.questions.all()
            serializer = SolutionQuestionSerializer(solution_questions, many=True)

    return JsonResponse({'results': serializer.data})
