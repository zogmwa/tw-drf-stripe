import stripe
from django.conf import settings
from djstripe import webhooks
from djstripe.models import Product
from djstripe.models import Price
from djstripe.models import Event
from djstripe.models import Invoice
from djstripe.models import Subscription

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
    When the new price is created, we create the price in db(sync) and  update the stripe_primary_price of a solution
    which corresponds to the product which is linked with this new price to the price
    """

    price_data = event.data
    price = Price.sync_from_stripe_data(price_data['object'])

    product = price.product
    solution, _ = Solution.objects.get_or_create(stripe_product=product)
    solution.is_published = False
    solution.stripe_primary_price = price
    solution.save()


@webhooks.handler('price.updated')
def price_updated_handler(event, **kwargs):
    price_data = event.data
    price = Price.sync_from_stripe_data(price_data['object'])
    solution = Solution.objects.get(stripe_product=price.product)

    # if the price is archived and is the stripe_primary_price of solution, we set stripe_primary_price to None
    if price.active is False and solution.stripe_primary_price == price:
        Solution.objects.filter(stripe_product=price.product).update(
            stripe_primary_price=None,
        )


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

    if product.metadata['tweb_type'] == 'solution':
        solution, is_created = Solution.objects.get_or_create(stripe_product=product)
        _set_solution_fields_from_product_instance(solution, product, is_created)


@webhooks.handler('product.updated')
def product_updated_handler(event: Event, **kwargs):
    """
    When the product is updated, we update the title, slug and also description(if the description is not
    already set) of the solution corresponding to the product which is ucreate_solutions_from_products.pypdated
    """
    product = Product.sync_from_stripe_data(event.data['object'])

    # In most cases is_created will be False because the product will already have a corresponding solution, however,
    # for some cases where there is a drift where product.created event did not trigger the handler or errored/server
    # was down, we can create the solution during the product update.
    if product.metadata['tweb_type'] == 'solution':
        solution, is_created = Solution.objects.get_or_create(stripe_product=product)
        _set_solution_fields_from_product_instance(
            solution, product, is_created=is_created
        )


@webhooks.handler('customer.subscription.updated')
def subscription_updated_handler(event: Event, **kwargs):
    """
    When the subscription is updated, we should sync the subscription data from stripe.
    """
    subscription_data = event.data
    Subscription.sync_from_stripe_data(subscription_data['object'])


@webhooks.handler('invoice')
def invoice_webhook_handler(event: Event, **kwargs):
    # first retrieve the Stripe Data Object (this is not a python dict or a JSON object.)
    invoice_data = stripe.Invoice.retrieve(event.data["object"]["id"])

    # sync_from_stripe_data to save it to the database,
    # and recursively update any referenced objects
    Invoice.sync_from_stripe_data(invoice_data)


def _get_slug_from_solution_title(solution_title: str) -> str:
    if settings.STRIPE_LIVE_MODE:
        solution_slug = slugify(solution_title[:200])
    else:
        # Prefixing test to test mode slugs so that there is no slug collision when we copy over solution to live mode
        # slug is a unique field
        solution_slug = slugify('test-{}'.format(solution_title)[:200])
    return solution_slug
