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


class TestSolutionPromoVideoField:
    def test_create_solution_updates_promo_video_to_embedable_url(self):
        non_embedable_promo_video_link = 'http://www.youtube.com/watch?v=Q0hi9d1W3Ag'
        expected_embedable_link = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        solution = Solution.objects.create(
            slug='test-solution',
            title='Test Solution',
            type='I',
            description='bla bla bla',
            scope_of_work='bla bla bla',
            promo_video=non_embedable_promo_video_link,
        )
        assert solution.promo_video == expected_embedable_link

    def test_addition_of_promo_video_on_existing_solution(self):
        non_embedable_promo_video_link = 'http://www.youtube.com/watch?v=Q0hi9d1W3Ag'
        expected_embedable_link = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        solution = Solution.objects.create(
            slug='test-solution',
            title='Test Solution',
            type='I',
            description='bla bla bla',
            scope_of_work='bla bla bla',
        )
        solution.promo_video = non_embedable_promo_video_link
        solution.save()
        assert solution.promo_video == expected_embedable_link

    def test_addition_of_embedable_promo_video(self):
        embedable_link = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        solution = Solution.objects.create(
            slug='test-solution',
            title='Test Solution',
            type='I',
            description='bla bla bla',
            scope_of_work='bla bla bla',
            promo_video=embedable_link,
        )
        assert solution.promo_video == embedable_link

    def test_addition_of_embedable_promo_video_without_https_prefix(self):
        form_url = 'www.youtube.com/embed/Q0hi9d1W3Ag'
        solution = Solution.objects.create(
            slug='test-solution',
            title='Test Solution',
            type='I',
            description='bla bla bla',
            scope_of_work='bla bla bla',
            promo_video=form_url,
        )

        expected_embed_url = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        assert solution.promo_video == expected_embed_url

    def test_https_prefix_is_added_for_non_https_urls(self):
        form_url = 'http://www.youtube.com/embed/Q0hi9d1W3Ag'
        solution = Solution.objects.create(
            slug='test-solution',
            title='Test Solution',
            type='I',
            description='bla bla bla',
            scope_of_work='bla bla bla',
            promo_video=form_url,
        )

        expected_embed_url = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        assert solution.promo_video == expected_embed_url
