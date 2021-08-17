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
from .tag import Tag


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

    # An attribute is kind of like a feature tag or a highlight, example "Easy to Use" is an attribute
    attributes = models.ManyToManyField(Attribute, through='LinkedAttribute', related_name='assets')
    # questions: to fetch all questions related to this asset

    promo_video = models.URLField(max_length=2048, null=True, blank=True)

    tweb_url_clickthrogh_counter = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)

    # Which user owns this Asset/Web Service (intended for web service owners)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='owned_assets',
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='submitted_assets',
    )
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)

    @property
    def upvotes_count(self):
        return self.votes.filter(is_upvote=True).count()

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

    @staticmethod
    def get_embed_video_url(video_url):
        if video_url is None:
            return video_url

        """ Takes a URL string for a video and converts it into an embeddeable video link """
        if '//' not in video_url:
            video_url = "https://{}".format(video_url)

        f = furl(video_url)

        if 'youtu.be' in f.netloc:
            # For youtu.be links the video id is in the path
            embed_url = 'https://www.youtube.com/embed' + str(f.path)
        elif 'youtube.com' in f.netloc and not str(f.path).startswith('/embed'):
            vid = f.args['v']
            embed_url = 'https://www.youtube.com/embed/{}'.format(vid)
        elif "vimeo.com" in f.netloc and not str(f.path).startswith('/video'):
            # Vimeo also keeps video id in the path
            embed_url = 'https://player.vimeo.com/video' + str(f.path)
        else:
            # If the scheme was http then override it with https
            f.scheme = 'https'
            embed_url = f.url

        return embed_url

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

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Web Service'
        verbose_name_plural = 'Web Services'


@receiver(pre_save, sender=Asset)
def asset_conditional_updates(sender, instance=None, **kwargs):
    """
    Performs some checks to compare old asset state with new asset state and perform conditional field update logic.
    Conditional updates help because they reduce average write time when saving many objects.
    """

    try:
        instance_old = sender.objects.get(pk=instance.pk)
        if instance.promo_video and instance_old.promo_video is None:
            # Only update the promo video if old video link was not set and the new is set
            instance.promo_video = sender.get_embed_video_url(instance.promo_video)
    except sender.DoesNotExist:
        # If it's a new asset/web-service being created for which an old one does not exist then
        # we still want to update the promo video
        instance.promo_video = sender.get_embed_video_url(instance.promo_video)
