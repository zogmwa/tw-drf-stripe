from rest_framework.serializers import ModelSerializer
from api.models import UserProblem
from api.serializers.user import UserSerializer


class UserProblemSerializer(ModelSerializer):
    class Meta:
        model = UserProblem
        fields = ['email', 'description', 'searched_term', 'user']

    user = UserSerializer(read_only=True)

    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            # Set the user to the logged in user, because that is whom the submitted problem will be associated with
            validated_data['user'] = request.user

        return super().create(validated_data)
