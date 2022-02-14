from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from api.serializers.consultation_request import (
    ConsultationRequestSerializer,
    ReadConsultationRequestSerializer,
)
from api.models.consultation_request import ConsultationRequest


class ConsultationRequestViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ConsultationRequest.objects.all()
    serializer_class = ConsultationRequestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "solution__id",
        "solution__slug",
    ]
    lookup_field = "id"
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if not self.action == 'create':
            return ReadConsultationRequestSerializer
        return super().get_serializer_class()
