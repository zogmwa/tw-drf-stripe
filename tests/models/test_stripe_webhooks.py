from api.models import Solution
from api.models.webhooks_stripe import (
    price_created_handler,
    product_created_handler,
    _get_slug_from_solution_title,
)
from djstripe.models import Price, Product
from django.utils.text import slugify


class TestStripeWebhooksProductPrice:
    def test_create_product_webhook_should_create_solution(
        self, example_stripe_product_create_event
    ):
        product_created_handler(example_stripe_product_create_event)
        product = Product.objects.get(
            id=example_stripe_product_create_event['data']['id']
        )
        solution = Solution.objects.get(stripe_product_id=product.pk)

        solution_slug = _get_slug_from_solution_title(product.name[:200])
        assert solution.title == product.name
        assert solution.description == product.description
        assert solution.slug == solution_slug

    def test_create_price_webhook_should_sync_price_in_db(
        self, example_stripe_price_create_event
    ):
        price_created_handler(example_stripe_price_create_event)

        assert Price.objects.all().count() == 1

        price = Price.objects.get(id=example_stripe_price_create_event['data']['id'])
        assert price is not None

    def test_create_price_webhook_should_link_this_price_to_solution(
        self, example_stripe_price_create_event
    ):
        price_created_handler(example_stripe_price_create_event)

        djstripe_price = Price.objects.get(
            id=example_stripe_price_create_event['data']['id']
        )
        djstripe_product = Product.objects.get(
            id=example_stripe_price_create_event['data']['product']
        )

        solution = Solution.objects.get(stripe_product_id=djstripe_product.pk)
        assert solution.pay_now_price == djstripe_price
