from api.models import Solution
from api.models.webhooks_stripe import (
    price_created_handler,
    product_created_handler,
    product_updated_handler,
    _get_slug_from_solution_title,
    price_updated_handler,
    price_deleted_handler,
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
        assert solution.description == solution.stripe_product.description

    def test_product_update_webhook_should_update_solution(
        self, example_stripe_product_create_event
    ):
        # first product.created webhook will be fired after that product.updated webhook will be called
        product_created_handler(example_stripe_product_create_event)
        product_dict = example_stripe_product_create_event.data["object"]

        updated_name = "updated name of product"
        updated_description = "updated description of product"
        old_description = product_dict["description"]

        stripe_product_update_event = example_stripe_product_create_event
        product_dict["name"] = updated_name
        product_dict["description"] = updated_description
        stripe_product_update_event.data["ojbect"] = product_dict

        product_updated_handler(example_stripe_product_create_event)

        solution = Solution.objects.get(stripe_product__id=product_dict['id'])
        solution_slug = _get_slug_from_solution_title(product_dict["name"][:200])
        assert solution.slug == solution_slug
        assert solution.title == updated_name
        # description should not be changed when product is being updated
        assert solution.description == old_description

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

    def test_price_deleted_webhook_should_delete_price_and(
        self, example_stripe_price_delete_event
    ):
        price_deleted_handler(example_stripe_price_delete_event)
        assert Price.objects.all().count() == 0

    def test_price_updated_webhook_should_update_djstripe_price(
        self, example_stripe_price_create_event
    ):
        price_dict = example_stripe_price_create_event.data['object']
        price_created_handler(example_stripe_price_create_event)

        stripe_price_update_event = example_stripe_price_create_event
        updated_unit_amount = 20000
        stripe_price_update_event.data['object']['unit_amount'] = updated_unit_amount

        price_updated_handler(stripe_price_update_event)
        price = Price.objects.get(id=price_dict['id'])
        assert price.unit_amount == updated_unit_amount

    def test_when_price_is_archived_pay_now_price_for_solution_should_be_set_to_none(
        self,
        example_stripe_price_create_event,
        example_stripe_price_archive_event,
        example_stripe_product_create_event,
    ):
        price_dict = example_stripe_price_create_event.data['object']
        product_created_handler(example_stripe_product_create_event)
        price_created_handler(example_stripe_price_create_event)
        price = Price.objects.get(id=price_dict['id'])

        solution = Solution.objects.get(stripe_product=price.product)
        assert solution.pay_now_price == price
        price_updated_handler(example_stripe_price_archive_event)
        solution = Solution.objects.get(stripe_product=price.product)
        assert solution.pay_now_price is None
