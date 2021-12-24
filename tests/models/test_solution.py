import pytest

from api.models import Solution
from djstripe.models import Product as StripeProduct


class TestSolutionCreateWithStripeProduct:
    @pytest.mark.skip(reason="syncing style is changed, no need for this test now")
    def test_if_solution_title_and_description_are_used_from_underlying_stripe_product(
        self, admin_user
    ):
        product = StripeProduct(
            name='test stripe product',
            id='prod_KkGmWqkik2VpYo',
        )
        product.save()
        solution = Solution.objects.create(
            slug='test-solution',
            title='Test Solution',
            type='I',
            description='bla bla bla',
            scope_of_work='bla bla bla',
            point_of_contact=admin_user,
            stripe_product=product,
        )
        solution_pk = solution.pk
        assert solution.title == product.name
        product.name = 'updated stripe product name'
        product.save()
        solution = Solution.objects.get(pk=solution_pk)
        solution.save()
        solution = Solution.objects.get(pk=solution_pk)
        assert solution.title == product.name
