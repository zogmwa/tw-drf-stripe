from django.conf import settings
from django.db import models

from api.models import Solution


class SolutionQuestion(models.Model):
    """
    A frequently-asked or user question related to an solution for which they seek an answer.
    The questions can be user submitted or added by a moderator for informational purposes
    """

    solution = models.ForeignKey(
        Solution, related_name='questions', on_delete=models.CASCADE
    )
    title = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # There might be an open question that is not answered yet
    # This is the primary answer because later we may introduce a separate answer model with multiple answers possible
    # for the same question. This is the answer which will be highlighted below the question.
    primary_answer = models.TextField(null=True, blank=True)

    # The user who submitted this question, if this is submitted by a moderator or is anonymous, this can be blank
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'Solution Question'
        verbose_name_plural = 'Solution Questions'

    def __str__(self):
        return "{}: {}".format(self.solution.title, self.title)
