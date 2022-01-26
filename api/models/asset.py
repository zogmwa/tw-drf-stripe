import os
import logging
from urllib.error import HTTPError

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from furl import furl
from opengraph import OpenGraph
from opengraphio import OpenGraphIO

from .asset_attribute import Attribute
from .solution import Solution
from .tag import Tag
from .organization import Organization
from api.utils.promo_video_conditional_updates_signal import (
    promo_video_conditional_updates,
)


def _upload_to_for_logos(instance, filename):
    path = "images/logos/"
    filename_with_extension = "{}.{}".format(
        instance.slug, instance.logo.file.image.format.lower()
    )
    return os.path.join(path, filename_with_extension)


class Asset(models.Model):
    """
    Asset for now represents a web asset such as a website, software, application or web offering.
    """

    slug = models.SlugField(null=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(max_length=2048, null=True, blank=True)

    # OpenGraph og:image url. This can be used as the primary snapshot url
    og_image_url = models.URLField(max_length=2048, null=True, blank=True)

    # This is a referral link to that asset, to be used in preference over regular web link
    # when it is set to a non-empty value
    affiliate_link = models.URLField(max_length=2048, null=True, blank=True)

    # Later on we can have image field as well but for now to avoid storing images
    # we can pull the logo directly from the respective site
    logo_url = models.URLField(max_length=2048, null=True, blank=True)

    # To be used as a fallback for logo_url if it's unset.
    # User's should both be able to upload a logo or specify a logo_url
    logo = models.ImageField(null=True, blank=True, upload_to=_upload_to_for_logos)

    pricing_url = models.URLField(
        max_length=200,
        null=True,
        blank=True,
        help_text=(
            'Optional link to page with more information (for clickable pricing table'
            ' headers)'
        ),
    )
    # The company that is providing this application or software
    company = models.CharField(max_length=255, null=True, blank=True)

    short_description = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    has_free_trial = models.BooleanField(default=False)
    trial_days = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, through='LinkedTag', related_name='assets')
    solutions = models.ManyToManyField(
        Solution, through='LinkedSolution', related_name='assets'
    )

    # An attribute is kind of like a feature tag or a highlight, example "Easy to Use" is an attribute
    attributes = models.ManyToManyField(
        Attribute, through='LinkedAttribute', related_name='assets'
    )
    # questions: to fetch all questions related to this asset

    promo_video = models.URLField(max_length=2048, null=True, blank=True)

    tweb_url_clickthrogh_counter = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)

    # Which user owns this Asset/Software (intended for software owners)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='owned_assets',
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='submitted_assets',
    )
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)
    avg_rating = models.DecimalField(default=0, decimal_places=7, max_digits=10)
    reviews_count = models.IntegerField(default=0)
    upvotes_count = models.IntegerField(default=0)
    is_homepage_featured = models.BooleanField(default=False, db_index=True)

    # Which organization owns this Asset (different from the owner which is a specific user at the organization
    # which owns this)
    owner_organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assets',
    )

    # Which organizations are the customers of this asset
    customer_organizations = models.ManyToManyField(
        Organization,
        through='OrganizationUsingAsset',
        related_name='assets_used',
        blank=True,
    )

    @property
    def users_count(self):
        return self.users.count()

    @property
    def tweb_url(self):
        """A masked TaggedWeb URL to allow tracking how many clicks each affiliate link/website is getting"""
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
                    opengraph = OpenGraphIO(
                        {'app_id': '8046bf50-dd39-4e7f-8988-8e8667387ff9'}
                    )
                    site_info = opengraph.get_site_info(passed_url=self.website)
                    hybrid_graph_dict = site_info['hybridGraph']
                    self.description = hybrid_graph_dict.get('description', '')
                    self.og_image_url = hybrid_graph_dict.get('image')

            if not self.logo_url:
                furled_url = furl(self.website)
                self.logo_url = 'https://logo.clearbit.com/{}'.format(furled_url.netloc)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Software'
        verbose_name_plural = 'Softwares'


pre_save.connect(promo_video_conditional_updates, sender=Asset)
