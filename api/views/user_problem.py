from rest_framework import viewsets, permissions

from api.models.user_problem import UserProblem
from api.serializers.user_problem import UserProblemSerializer


class UserProblemViewSet(viewsets.ModelViewSet):
    queryset = UserProblem.objects.all()
    serializer_class = UserProblemSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']
