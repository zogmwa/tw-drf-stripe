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
        response = product_created_handler(example_stripe_product_create_event)
        product_dict = example_stripe_product_create_event.data["object"]

        solution = Solution.objects.get(stripe_product__id=product_dict['id'])
        solution_slug = _get_slug_from_solution_title(solution.title[:200])
        assert solution.slug == solution_slug
        assert solution.title == solution.stripe_product.name

    def test_create_price_webhook_should_sync_price_in_db(
        self, example_stripe_price_create_event
    ):
        price_created_handler(example_stripe_price_create_event)

        assert Price.objects.all().count() == 1

        price_dict = example_stripe_price_create_event.data['object']
        # The following should not return a get error (get returns atleast one object or errors out)
        Price.objects.get(id=price_dict['id'])

    def test_create_price_webhook_should_link_this_price_to_solution(
        self, example_stripe_price_create_event
    ):
        price_created_handler(example_stripe_price_create_event)

        stripe_price_dict = example_stripe_price_create_event.data['object']
        price = Price.objects.get(id=stripe_price_dict['id'])
        product = Product.objects.get(id=stripe_price_dict['product'])

        solution = Solution.objects.get(stripe_product=product)
        assert solution.pay_now_price == price
