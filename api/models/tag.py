from django.db import models
from django.core.exceptions import ValidationError


def validate_positive_number(value):
    if value >= 0:
        return value
    else:
        raise ValidationError(
            "Value of counter can not be negative, please check overflow condition"
        )


class Tag(models.Model):
    slug = models.SlugField(null=True)
    name = models.CharField(max_length=255, unique=True)
    counter = models.BigIntegerField(default=0, validators=[validate_positive_number])
    description = models.CharField(max_length=1024, blank=True, null=True)
    is_homepage_featured = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name
