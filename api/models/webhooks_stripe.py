from django.conf import settings
from django.http import HttpResponse
from djstripe import webhooks
from djstripe.models import Product
from djstripe.models import Price
from djstripe.models import Event
from rest_framework.status import HTTP_200_OK

from api.models.solution import Solution
from django.utils.text import slugify


@webhooks.handler('price.created')
def price_created_handler(event, **kwargs):
    """
    When the new price is created, we create the price in db(sync) and  update the pay_now_price of a solution
    which corresponds to the product which is linked with this new price to the price
    """

    price_data = event.data
    price = Price.sync_from_stripe_data(price_data['object'])

    product = price.product
    solution, _ = Solution.objects.get_or_create(stripe_product=product)
    solution.title = product.name
    solution.slug = _get_slug_from_solution_title(solution.title)
    solution.is_published = False
    solution.pay_now_price = price
    solution.save()


@webhooks.handler('product.created')
def product_created_handler(event: Event, **kwargs):
    """
    When the new product is created, we create the price in db(sync) and  update the pay_now_price of a solution
    which corresponds to the product which is linked with this new price to the price
    """

    product = Product.sync_from_stripe_data(event.data['object'])

    solution, is_created = Solution.objects.get_or_create(stripe_product=product)
    solution.title = product.name
    solution.slug = _get_slug_from_solution_title(solution.title)
    solution.is_published = False

    if solution.description is None:
        solution.description = product.description

    solution.save()


def _get_slug_from_solution_title(solution_title: str) -> str:
    if settings.STRIPE_LIVE_MODE:
        solution_slug = slugify(solution_title[:200])
    else:
        # Prefixing test to test mode slugs so that there is no slug collision when we copy over solution to live mode
        # slug is a unique field
        solution_slug = slugify('test-{}'.format(solution_title)[:200])
    return solution_slug
