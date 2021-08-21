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

    def __str__(self):
        return self.name
