from rest_framework import viewsets, permissions

from api.models.newsletter_contact import NewsLetterContact
from api.serializers.newsletter_contact import NewsLetterContactSerializer


class NewsLetterContactViewSet(viewsets.ModelViewSet):
    queryset = NewsLetterContact.objects.all()
    serializer_class = NewsLetterContactSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post', 'head']
