from django.conf import settings
from django.db import models

from api.models.organization import Organization
from api.models.tag import Tag


class Solution(models.Model):
    """
    A solution can be an integration support/solution, usage support, or some other form solution/support
    related to one or more web service(s), which is provided by a specific organization or a user.
    """

    slug = models.SlugField(null=True, unique=True)

    # Every solution will have a corresponding product offering on Stripe
    stripe_product_id = models.CharField(null=True, blank=True, max_length=100)

    # Same be kept same as the stripe Product name where possible
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    scope_of_work = models.TextField(blank=True, null=True)

    class Type(models.TextChoices):
        INTEGRATION = 'I'
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

    # Max number of solution bookings that can be in pending/non-active state. Once the existing solution bookings count
    # hits the max queue size then we will not be allowing more solutions to be booked.
    max_queue_size = models.IntegerField(default=10)

    tags = models.ManyToManyField(
        Tag, through='LinkedSolutionTag', related_name='solutions'
    )

    is_published = models.BooleanField(default=True)

    primary_tag = models.ForeignKey(
        Tag, null=True, blank=True, on_delete=models.SET_NULL
    )

    upvotes_count = models.IntegerField(default=0)

    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'
