from django.db import models
from api.models import Solution


class ConsultationRequest(models.Model):
    solution = models.ForeignKey(
        Solution, related_name="consultation_requests", on_delete=models.CASCADE
    )

    customer_email = models.EmailField(max_length=2048)
    customer_first_name = models.CharField(max_length=255)
    customer_last_name = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solution Consultation Request"
        verbose_name_plural = "Solution Consultation Requests"
