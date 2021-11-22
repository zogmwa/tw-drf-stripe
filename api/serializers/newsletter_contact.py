from rest_framework.serializers import ModelSerializer

from api.models import NewsLetterContact


class NewsLetterContactSerializer(ModelSerializer):
    class Meta:
        model = NewsLetterContact
        fields = [
            'email',
        ]
