from rest_framework import viewsets, permissions

from api.models.submitted_problem import SubmittedProblem
from api.serializers.submitted_problem import SubmittedProblemSerializer


class SubmittedProblemViewSet(viewsets.ModelViewSet):
    queryset = SubmittedProblem.objects.all()
    serializer_class = SubmittedProblemSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']
