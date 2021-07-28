from django.db import models


class Tag(models.Model):
    slug = models.SlugField(null=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
