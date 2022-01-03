import pytest
from django.db.models.signals import post_save, pre_save
from django.core.signals import request_finished
from api.models.solution import (
    generate_solution_detail_pages_sitemap_files_pre_save,
    generate_solution_detail_pages_sitemap_files_post_save,
)

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
        post_save.disconnect(
            generate_solution_detail_pages_sitemap_files_post_save, sender=Solution
        )
        pre_save.disconnect(
            generate_solution_detail_pages_sitemap_files_pre_save, sender=Solution
        )
        request_finished.disconnect(
            generate_solution_detail_pages_sitemap_files_post_save,
            dispatch_uid="generate_solution_detail_pages_sitemap_files",
        )
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
