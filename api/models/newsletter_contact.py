from django.db import models


class NewsLetterContact(models.Model):
    email = models.EmailField(unique=True, max_length=254)

    def __str__(self):
        return self.email
