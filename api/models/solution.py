from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from djstripe.models import Product as StripeProduct
from djstripe.models import Price as StripePrice

from django.dispatch import receiver
from api.models.organization import Organization
from api.models.tag import Tag

from django.db.models.signals import post_save


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

    # The price the user will pay if they decide to pay upfront
    # This can be nullable because not all solutions will have pay now enabled. Some solutions require incremental
    # billing.
    pay_now_price = models.OneToOneField(
        StripePrice, null=True, blank=True, on_delete=models.SET_NULL
    )

    @property
    def pay_now_price_stripe_id(self) -> str:
        # This is needed by the frontend for the "Purchase Now" -> "Stripe Checkout" flow.
        return self.pay_now_price.id if self.pay_now_price else None

    @property
    def pay_now_price_unit_amount(self) -> str:
        # This will be in cents so frontend will have to divide this by 100 to show dollar value for USD
        return self.pay_now_price.unit_amount if self.pay_now_price else None

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    scope_of_work = models.TextField(blank=True, null=True)
    avg_rating = models.DecimalField(default=0, decimal_places=7, max_digits=10)
    reviews_count = models.IntegerField(default=0)
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

    # The user who will either be providing the support or be the point of contact at the organization providing
    # the support.
    point_of_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
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

    is_searchable = models.BooleanField(default=True)

    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'
