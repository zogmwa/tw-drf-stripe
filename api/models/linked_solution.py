from django.db import models

from api.models import Asset
from api.models.solution import Solution


class LinkedSolution(models.Model):
    """
    M2M Model that links solutions with an assets
    """

    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
