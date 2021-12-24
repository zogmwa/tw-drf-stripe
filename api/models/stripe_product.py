from django.db.models.signals import post_save
from django.dispatch import receiver
from djstripe.models import Product as StripeProduct
from djstripe.models import Price
from api.models.solution import Solution
from djstripe import webhooks
from django.utils.text import slugify


@receiver(post_save, sender=StripeProduct)
def sync_solution_instance_with_stripe_product(sender, instance=None, **kwargs):
    # import pdb
    #
    # pdb.set_trace()
    try:
        '''
        In updating the solution, we will not change the description. The description will be set to the description of the
        stripe product only when solution is created as a placeholder for more detailed description which will be added in
        future. The reason behind not having the detailed description on the Stripe Product instance itself is small size
        of the description field of stripe product description.
        '''
        solution = Solution.objects.get(stripe_product_id=instance.pk)
        solution.title = instance.name
        solution_slug = (
            instance.name[:200] if len(instance.name) > 200 else instance.name
        )
        solution.slug = solution_slug
        solution.save()
    except Solution.DoesNotExist:
        print('does not exist')
        solution_slug = (
            instance.name[:200] if len(instance.name) > 200 else instance.name
        )
        Solution.objects.create(
            title=instance.name,
            stripe_product_id=instance.pk,
            slug=slugify(solution_slug),
        )
        print('created')


@receiver(post_save, sender=Price)
def sync_solution_instance_with_stripe_product(sender, instance=None, **kwargs):
    '''
    Here we don't need to check if the solution exists or not because Product is always created first by djstripe, and
    in the post_save signal of StripeProduct, we've created Solution instance. In this signal we will update the pay_now_price
    of the solution to the latest price created for the Stripe Product.
    '''
    solution = Solution.objects.get(stripe_product_id=instance.product.pk)
    solution.pay_now_price = instance
    solution.save()
