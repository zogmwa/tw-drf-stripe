import logging
from urllib.error import HTTPError

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseForbidden
from guardian.mixins import GuardianUserMixin
from rest_framework.authtoken.models import Token

from furl import furl
from opengraph import OpenGraph

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
    slug = models.SlugField(null=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(max_length=2048, null=True, blank=True)

    # This is a referral link to that asset, to be used in preference over regular web link
    # when it is set to a non-empty value
    affiliate_link = models.URLField(max_length=2048, null=True, blank=True)

    # Later on we can have image field as well but for now to avoid storing images
    # we can pull the logo directly from the respective site
    logo_url = models.URLField(max_length=2048, null=True, blank=True)

    # The company that is providing this application or software
    company = models.CharField(max_length=255, null=True, blank=True)

    short_description = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, through='LinkedTag', related_name='assets')
    # questions: to fetch all questions related to this asset

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.website:
            if not self.short_description:
                try:
                    og_dict: dict = OpenGraph(url=self.website)

                    # https://ogp.me/ OpenGraph descriptions are short one-two sentences.
                    self.short_description = og_dict.get('description', '')
                except HTTPError as e:
                    # Some websites have same origin policy even for accessing OGP tags so trying to parse
                    # from their url may result in a forbidden error
                    logging.exception(e)

            if not self.logo_url:
                furled_url = furl(self.website)
                self.logo_url = 'https://logo.clearbit.com/{}'.format(furled_url.netloc)

        super(Asset, self).save(*args, **kwargs)


class AssetQuestion(models.Model):
    """
    A frequently-asked or user question related to an asset for which they seek an answer.
    The questions can be user submitted or added by a moderator for informational purposes
    """
    asset = models.ForeignKey(Asset, related_name='questions', on_delete=models.CASCADE)
    question = models.TextField()
    # There might be an open question that is not answered yet
    answer = models.TextField(null=True, blank=True)

    # The user who submitted this question, if this is submitted by a moderator or is anonymous, this can be blank
    submitted_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)

    # Number of users who have shown interest in this question by up-voting it (one user should only be able to upvote
    # this once - probably need a separate model to track UpVotes, this is just a summary count)
    upvote_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return "{}: {}".format(self.asset.name, self.question)


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
    api_daily_rate_limit = models.IntegerField(default=2000)

    def __str__(self):
        return '{}'.format(self.username,)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)


def get_anonymous_user_instance(user_class):
    """
    Added just to comply with: https://django-guardian.readthedocs.io/en/stable/userguide/custom-user-model.html
    """
    return user_class(username='AnonymousUser')
