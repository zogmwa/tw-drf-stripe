from django.db import models
from django.conf import settings


class UserProblem(models.Model):
    email = models.EmailField(max_length=254)
    description = models.TextField()
    searched_term = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_acknowledged = models.BooleanField(
        default=False, help_text='Whether this request has been addressed or not'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_problems',
    )

    class Meta:
        verbose_name = 'User Problem'
        verbose_name_plural = 'User Problems'

    def __str__(self):
        return self.email
