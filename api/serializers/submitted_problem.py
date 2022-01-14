from rest_framework.serializers import ModelSerializer

from api.models import SubmittedProblem


class SubmittedProblemSerializer(ModelSerializer):
    class Meta:
        model = SubmittedProblem
        fields = ['email', 'problem_title', 'searched_term']
