from djstripe.models import Price

from api.models.solution import Solution
from django.utils.text import slugify


class TestSolutionProductSync:
    def test_create_solution_when_new_stripe_product_is_created(
        self, example_stripe_product, example_stripe_price
    ):
        assert Solution.objects.all().count() == 1
        solution = Solution.objects.get(stripe_product=example_stripe_product)
        assert solution.stripe_product == example_stripe_product
        assert solution.pay_now_price == example_stripe_price
        solution_slug = slugify(
            example_stripe_product.name[:200]
            if len(example_stripe_product.name) > 200
            else example_stripe_product.name
        )
        assert solution.slug == solution_slug
        assert solution.description == example_stripe_product.description

    def test_updating_description_of_stripe_product_should_not_change_solution_desciption(
        self, example_stripe_product, example_stripe_price
    ):
        updated_description = 'new description of stripe product'
        example_stripe_product.description = updated_description
        example_stripe_product.save()
        solution = Solution.objects.get(stripe_product=example_stripe_product)
        assert solution.description != updated_description

    def test_title_slug_should_be_changed_for_solution_when_stripe_product_id_updated(
        self, example_stripe_product, example_stripe_price
    ):
        new_name = 'new name of stripe product'
        example_stripe_product.name = new_name
        example_stripe_product.save()
        solution = Solution.objects.get(stripe_product=example_stripe_product)
        assert solution.title == new_name
        solution_slug = slugify(new_name[:200] if len(new_name) > 200 else new_name)
        assert solution.slug == solution_slug

    def test_when_new_price_for_stripe_product_is_created_it_should_be_linked_with_corresponding_solution(
        self, example_stripe_product, example_stripe_price
    ):
        solution = Solution.objects.get(stripe_product=example_stripe_product)
        assert solution.pay_now_price == example_stripe_price
        new_price = Price.objects.create(
            currency='usd',
            id='lksjdf',
            product_id=example_stripe_product.id,
            unit_amount=20000,
            unit_amount_decimal=20000.000000000000,
            active=True,
        )
        solution = Solution.objects.get(stripe_product=example_stripe_product)
        assert solution.pay_now_price == new_price

    def test_truncate_title_for_solution_slug(
        self, example_stripe_product, example_stripe_price
    ):
        new_title = ''
        for i in range(255):
            new_title = new_title + 'a'
        example_stripe_product.name = new_title
        example_stripe_product.save()
        solution = Solution.objects.get(stripe_product=example_stripe_product)
        assert len(solution.slug) == 200
