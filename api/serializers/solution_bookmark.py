from rest_framework.serializers import ModelSerializer

from api.models.solution_bookmark import SolutionBookmark
from api.serializers.solution import AuthenticatedSolutionForBookmarkSerializer


class SolutionBookmarkSerializer(ModelSerializer):
    solution = AuthenticatedSolutionForBookmarkSerializer(read_only=True)

    class Meta:
        model = SolutionBookmark
        fields = ['id', 'solution', 'user']
