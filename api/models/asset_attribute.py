from django.db import models
from django.conf import settings


class Attribute(models.Model):
    """
    An asset attribute is something that describes an asset like 'Easy to Use'. It's different from a tag
    in that rather than being a category tag it is kind of like a feature or highlight that
    acts as an adjective for the web service it is used on.
    """
    name = models.CharField(max_length=55, unique=True)

    # Default it is a positive attribute/pro, unless it's marked as a con/negative
    is_con = models.BooleanField(default=False)

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Web Service Attribute'
        verbose_name_plural = 'Web Service Attributes'

    def __str__(self):
        return self.name
