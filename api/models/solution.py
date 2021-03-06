import os
from django.conf import settings
from django.db import models
from djstripe.models import Product as StripeProduct
from djstripe.models import Price as StripePrice
from django.db.models.signals import pre_save
from django.db.models import Q
from django.apps import apps
from api.models.organization import Organization
from api.models.tag import Tag
from api.management.commands import generate_sitemap_solution_detail
from api.management.commands import generate_sitemap_index
from api.utils.promo_video_conditional_updates_signal import (
    promo_video_conditional_updates,
)


def _upload_to_for_cover_images(instance, filename):
    path = "solution/cover_images/"
    filename_with_extension = "{}.{}".format(
        str(instance.slug), instance.cover_image.file.image.format.lower()
    )

    return os.path.join(path, filename_with_extension)


class Solution(models.Model):
    """
    A solution can be an integration support/solution, usage support, or some other form solution/support
    related to one or more web service(s), which is provided by a specific organization or a user.
    """

    slug = models.SlugField(null=True, unique=True, max_length=200)

    # Every solution will have a corresponding product offering on Stripe
    stripe_product = models.OneToOneField(
        StripeProduct, null=True, blank=True, on_delete=models.SET_NULL
    )

    # For pre-paid solutions this is the price the user will pay if they decide to pay upfront
    # For metered-solutions this is the unit price (e.g. hourly price, etc) they will be billed at
    # (This can be nullable because when a solution is created this may not be set immediately)
    stripe_primary_price = models.OneToOneField(
        StripePrice, null=True, blank=True, on_delete=models.SET_NULL
    )

    @property
    def stripe_primary_price_stripe_id(self) -> str:
        # This is needed by the frontend for the "Purchase Now" -> "Stripe Checkout" flow.
        return self.stripe_primary_price.id if self.stripe_primary_price else None

    @property
    def stripe_primary_price_unit_amount(self) -> str:
        # This will be in cents so frontend will have to divide this by 100 to show dollar value for USD
        return (
            self.stripe_primary_price.unit_amount if self.stripe_primary_price else None
        )

    @property
    def capacity_used(self) -> int:
        solution_booking = apps.get_model('api', 'SolutionBooking')
        return self.bookings.filter(
            ~Q(status=solution_booking.Status.COMPLETED), is_payment_completed=True
        ).count()

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    scope_of_work = models.TextField(blank=True, null=True)

    sad_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)
    happy_count = models.IntegerField(default=0)
    consultation_scheduling_link = models.URLField(
        blank=True, null=True, max_length=255
    )

    class Type(models.TextChoices):
        INTEGRATION = 'I'
        CONSULTATION = 'C'
        # Usage support is kind of like a consultation but still putting it into it's own category
        USAGE_SUPPORT = 'U'
        OTHER = 'O'

    type = models.CharField(
        max_length=2, choices=Type.choices, default=Type.INTEGRATION
    )

    # There may or may not be an organization providing this solution (in that case point_of_contact user will be
    # providing the support)
    organization = models.ForeignKey(
        Organization, blank=True, null=True, on_delete=models.SET_NULL
    )

    cover_image = models.ImageField(
        null=True, blank=True, upload_to=_upload_to_for_cover_images
    )
    promo_video = models.URLField(max_length=2048, null=True, blank=True)

    # The user who will either be providing the support or be the point of contact at the organization providing
    # the support.
    point_of_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    # Follow-On solutions a.k.a. Downstream solutions that are typically performed after Upstream solutions
    follow_on_solutions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='upstream_solutions',
        blank=True,
    )

    # Solution.assets will give the related assets (via related_name='solutions' on Asset model)

    # Estimated number of days it will take to fully deliver the solution to the customer
    eta_days = models.IntegerField(null=True, blank=True, verbose_name='ETA Days')

    # Hourly contract rate for follow-up engagement on unscoped work after the solution (For case by case hourly rate,
    # leave this to null)
    follow_up_hourly_rate = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )

    # https://hackernoon.com/why-capacity-planning-needs-queueing-theory-without-the-hard-math-342a851e215c
    # Max number of solution bookings that are being actively worked on or the team has capacity to actively work on
    # in parallel.
    capacity = models.IntegerField(default=10)

    bookings_pending_fulfillment_count = models.IntegerField(default=0)

    # Max number of solution bookings that can be in pending/non-active state. Once the existing solution bookings count
    # hits the max queue size then we will not be allowing more solutions to be booked.
    max_queue_size = models.IntegerField(default=10)

    tags = models.ManyToManyField(
        Tag, through='LinkedSolutionTag', related_name='solutions'
    )
    has_free_consultation = models.BooleanField(default=False)

    is_published = models.BooleanField(default=True)

    primary_tag = models.ForeignKey(
        Tag, null=True, blank=True, on_delete=models.SET_NULL
    )

    upvotes_count = models.IntegerField(default=0)

    # Some solution links will be unlisted so we don't want to show them in the search but users should be able to
    # directly get to the links of such solutions.
    is_searchable = models.BooleanField(
        default=True,
        help_text='Do we want this solution to show up in search results? (Or be like an unlisted link)',
    )

    # Some solutions are metered billing solutions, so if solution is metered billing solution,
    # this field should be true.
    is_metered = models.BooleanField(
        default=False, help_text='This field can be update with updating stripe price'
    )

    # If solution is metered billing solution, this fields should be filling.
    team_size = models.IntegerField(blank=True, null=True)
    estimated_hours = models.IntegerField(blank=True, null=True)
    blended_hourly_rate = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )

    class BillingPeriodType(models.TextChoices):
        WEEKLY = 'Weekly '
        BIWEEKLY = 'Biweekly'
        MONTHLY = 'Monthly'

    billing_period = models.CharField(
        max_length=9,
        null=True,
        blank=True,
        choices=BillingPeriodType.choices,
        default=None,
    )

    # Some solutions will be mapped to test products (STRIPE_LIVE_MODE=False), we want to have a property field that
    # can be displayed as a read only field in admin for convenience.
    @property
    def livemode(self) -> bool:
        return self.stripe_product.livemode if self.stripe_product else None

    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'


def solution_detail_sitemap_generator():
    solution_detail_cmd = generate_sitemap_solution_detail.Command()
    sitemap_index_cmd = generate_sitemap_index.Command()
    solution_detail_cmd.handle(**{})
    sitemap_index_cmd.handle(**{})


pre_save.connect(promo_video_conditional_updates, sender=Solution)
