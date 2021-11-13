from django.db import models

from api.models.tag import Tag
from api.models.solution import Solution


class LinkedSolutionTag(models.Model):
    """
    M2M Model that links tags with an solutions
    """

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
