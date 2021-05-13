from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.mixins import GuardianUserMixin
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Tag(models.Model):
    slug = models.SlugField(null=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Asset(models.Model):
    """
    Asset for now represents a web asset such as a website, software, application or web offering.
    """
    slug = models.SlugField(null=True)
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=2048, null=True, blank=True)

    # Later on we can have image field as well but for now to avoid storing images
    # we can pull the logo directly from the respective site
    logo_url = models.URLField(max_length=2048, null=True, blank=True)

    # The company that is providing this application or software
    company = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, through='LinkedTag')

    def __str__(self):
        return self.name


class LinkedTag(models.Model):
    """
    M2M Model that links tags with an assets
    """
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)


class User(AbstractUser, GuardianUserMixin):
    """
    This is a TaggedWeb user, a user can be an administrator someone else who wants to submit their web asset
    for listing on TaggedWeb. A user can also be an application like our frontend application using our API token
    to fetch details about a web asset.
    """
    api_daily_rate_limit = models.IntegerField(default=1000)

    def __str__(self):
        return '{}'.format(self.username,)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)


def get_anonymous_user_instance(user_class):
    """
    Added just to comply with: https://django-guardian.readthedocs.io/en/stable/userguide/custom-user-model.html
    """
    return user_class(username='AnonymousUser')
