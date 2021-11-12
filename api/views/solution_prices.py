# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import viewsets, permissions
#
# from api.models.solution_price import SolutionPrice
# from api.serializers.solution_price import SolutionPriceSerializer
#
#
# class SolutionPriceViewSet(viewsets.ModelViewSet):
#
#     queryset = SolutionPrice.objects.filter()
#     permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = {
#         'created': ['gte', 'lte'],
#         'updated': ['gte', 'lte'],
#         'status': ['exact'],
#     }
#     serializer_class = SolutionPriceSerializer
