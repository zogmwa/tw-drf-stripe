from django.conf import settings
from djstripe import webhooks
from djstripe.models import Product
from djstripe.models import Price
from djstripe.models import Event

from api.models.solution import Solution
from django.utils.text import slugify


def _set_solution_fields_from_product_instance(
    solution: Solution,
    product: Product,
    is_created=False,
) -> None:
    solution.title = product.name
    slug_default_from_title = _get_slug_from_solution_title(solution.title)

    if is_created:
        # For updates we don't automatically want to update slugs because it may render the old url obsolete
        solution.slug = slug_default_from_title

        # Newly created solutions should by default be in unpublished state
        # Other solutions should retain their previous state
        solution.is_published = False
    else:
        if solution.slug is None:
            solution.slug = slug_default_from_title

    if solution.description is None:
        solution.description = product.description

    solution.save()


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
    solution.is_published = False
    solution.pay_now_price = price
    solution.save()


@webhooks.handler('price.updated')
def price_updated_handler(event, **kwargs):
    price_data = event.data
    price = Price.sync_from_stripe_data(price_data['object'])
    solution = Solution.objects.get(stripe_product=price.product)

    # if the price is archived and is the pay_now_price of solution, we set pay_now_price to None
    if price.active is False and solution.pay_now_price == price:
        Solution.objects.filter(stripe_product=price.product).update(pay_now_price=None)


@webhooks.handler('price.deleted')
def price_deleted_handler(event, **kwargs):
    price_dict = event.data['object']
    Price.objects.filter(id=price_dict['id']).delete()


@webhooks.handler('product.created')
def product_created_handler(event: Event, **kwargs):
    """
    When the new product is created, we create the solution which corresponds to the product and set
    title, description and slug of the solution
    """

    product = Product.sync_from_stripe_data(event.data['object'])

    solution, is_created = Solution.objects.get_or_create(stripe_product=product)
    _set_solution_fields_from_product_instance(solution, product, is_created)


@webhooks.handler('product.updated')
def product_updated_handler(event: Event, **kwargs):
    """
    When the product is updated, we update the title, slug and also description(if the description is not
    already set) of the solution corresponding to the product which is updated
    """
    product = Product.sync_from_stripe_data(event.data['object'])

    # In most cases is_created will be False because the product will already have a corresponding solution, however,
    # for some cases where there is a drift where product.created event did not trigger the handler or errored/server
    # was down, we can create the solution during the product update.
    solution, is_created = Solution.objects.get_or_create(stripe_product=product)
    _set_solution_fields_from_product_instance(solution, product, is_created=is_created)


def _get_slug_from_solution_title(solution_title: str) -> str:
    if settings.STRIPE_LIVE_MODE:
        solution_slug = slugify(solution_title[:200])
    else:
        # Prefixing test to test mode slugs so that there is no slug collision when we copy over solution to live mode
        # slug is a unique field
        solution_slug = slugify('test-{}'.format(solution_title)[:200])
    return solution_slug
