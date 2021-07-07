import logging
from urllib.error import HTTPError

from django.conf import settings
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from opengraphio import OpenGraphIO
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

    # OpenGraph og:image url
    og_image_url = models.URLField(max_length=2048, null=True, blank=True)

    # This is a referral link to that asset, to be used in preference over regular web link
    # when it is set to a non-empty value
    affiliate_link = models.URLField(max_length=2048, null=True, blank=True)

    # Later on we can have image field as well but for now to avoid storing images
    # we can pull the logo directly from the respective site
    logo_url = models.URLField(max_length=2048, null=True, blank=True)
    pricing_url = models.URLField(
        max_length=200,
        null=True,
        blank=True,
        help_text='Optional link to page with more information (for clickable pricing table headers)',
    )
    # The company that is providing this application or software
    company = models.CharField(max_length=255, null=True, blank=True)

    short_description = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, through='LinkedTag', related_name='assets')
    # questions: to fetch all questions related to this asset

    promo_video = models.URLField(max_length=2048, null=True, blank=True)

    tweb_url_clickthrogh_counter = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)

    # Which user owns this Asset/Web Service (intended for web service owners)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def upvotes_count(self):
        return self.votes.filter(upvote=True).count()

    @property
    def tweb_url(self):
        """ A masked TaggedWeb URL to allow tracking how many clicks each affiliate link/website is getting """
        final_url = self.affiliate_link or self.website
        if final_url:
            # /r/assets/{slug} stands for redirect asset with the given slug from this to third party url
            return "https://{}/r/assets/{}".format(settings.BASE_API_URL, self.slug)

    def __str__(self):
        return self.name

    def update_clickthrough_counter(self):
        self.tweb_url_clickthrogh_counter += 1
        self.save()

    def save(self, *args, **kwargs):
        if self.website:
            if not self.description:
                try:
                    og_dict: dict = OpenGraph(url=self.website)

                    # https://ogp.me/ OpenGraph descriptions are short one-two sentences.
                    self.description = og_dict.get('description', '')
                    self.og_image_url = og_dict.get('image')
                except HTTPError as e:
                    # Some websites have same origin policy even for accessing OGP tags so trying to parse
                    # from their url may result in a forbidden error
                    logging.exception(e)
                    opengraph = OpenGraphIO({'app_id': '8046bf50-dd39-4e7f-8988-8e8667387ff9'})
                    site_info = opengraph.get_site_info(passed_url=self.website)
                    hybrid_graph_dict = site_info['hybridGraph']
                    self.description = hybrid_graph_dict.get('description', '')
                    self.og_image_url = hybrid_graph_dict.get('image')

            if not self.logo_url:
                furled_url = furl(self.website)
                self.logo_url = 'https://logo.clearbit.com/{}'.format(furled_url.netloc)

        super(Asset, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Web Service'
        verbose_name_plural = 'Web Services'


class AssetVote(models.Model):
    # For now we will only have upvotes, no downvotes
    upvote = models.BooleanField(default=True, help_text='Whether this is an Upvote=true (or Downvote=false)')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='votes',
        on_delete=models.CASCADE,
    )
    voted_on = models.DateTimeField(auto_now_add=True)
    asset = models.ForeignKey(Asset, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.asset, self.user)

    class Meta:
        UniqueConstraint(fields=['asset', 'user'], name='user_asset_vote')
        verbose_name = 'Web Service Vote'
        verbose_name_plural = 'Web Service Votes'


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


class PricePlan(models.Model):
    """
    A price plan associated with an asset. An asset can have one or more price plans. If the price is 0,
    then the plan is free, if price is not set then the plan is a CUSTOM plan.
    """
    asset = models.ForeignKey(Asset, related_name='price_plans', on_delete=models.CASCADE)
    name = models.CharField(max_length=128, null=False, blank=False, help_text='Name of the Price Plan')
    summary = models.CharField(max_length=1024, blank=True, null=True)

    currency = models.CharField(max_length=3, default='USD')
    # Price along with the caveats price per month per user, price pear seat
    # This can be nullable because for Custom price plans, price is not known upfront
    price = models.CharField(max_length=16, null=True, blank=True)

    # Day, Month, Year, X Requests, User per Month
    per = models.CharField(max_length=32, null=True, blank=True)

    # This will contain bulleted features to be stored in Markdown format
    features = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Price Plan'
        verbose_name_plural = 'Price Plans'

    def __str__(self):
        return "{}: {} - {} {} per {}".format(self.asset.name, self.name, self.currency, self.price, self.per)


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
