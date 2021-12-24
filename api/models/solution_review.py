from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint, F
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.signals import request_finished

from api.models import Solution


class SolutionReview(models.Model):
    class Type(models.TextChoices):
        SAD = 'S'
        NEUTRAL = 'N'
        HAPPY = 'H'

    solution = models.ForeignKey(
        Solution, related_name='reviews', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='solution_reviews',
        # SET_NULL because we want to retain a review even if the corresponding user is deleted
        on_delete=models.SET_NULL,
    )

    type = models.CharField(max_length=2, choices=Type.choices)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}: {}".format(self.solution, self.user, self.type)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['solution', 'user', 'type'], name='user_solution_review'
            )
        ]
        verbose_name = 'Solution Review'
        verbose_name_plural = 'Solution Reviews'
