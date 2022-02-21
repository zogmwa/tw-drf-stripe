"""
Products refer to djstripe.models.Product instances which are 1:1 mapped to Stripe Products.
Normally for prod, products and corresponding solutiosn are automatically created from product.created webhooks.
For local though, we need to pull in data from stripe first and then run this code to use the stripe product and
create our wrapper Solution objects:

Example Usage:
    python manage.py djstripe_sync_models Product Price
    python create_solutions_from_products
"""

from django.core.management.base import BaseCommand
from djstripe.models import Product

from api.models import Solution
from api.models.webhooks_stripe import _set_solution_fields_from_product_instance


class Command(BaseCommand):
    help = (
        "Helps create local Solution instances from djstripe Product instances."
        "Make sure you run the python manage.py djstripe_sync_models Product Price before"
    )

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        for product in Product.objects.all():
            if product.metadata['tweb_type'] == 'solution':
                solution, is_created = Solution.objects.get_or_create(
                    stripe_product=product
                )
                _set_solution_fields_from_product_instance(
                    solution, product, is_created=is_created
                )
                solution.save()
