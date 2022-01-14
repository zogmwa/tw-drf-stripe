from django.db import models


class SubmittedProblem(models.Model):
    email = models.EmailField(unique=True, max_length=254)
    problem_title = models.TextField()
    searched_term = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_acknowledged = models.BooleanField(
        default=False, help_text='Whether this request has been addressed or not'
    )

    class Meta:
        verbose_name = 'Submitted Problem'
        verbose_name_plural = 'Submitted Problems'

    def __str__(self):
        return self.email
