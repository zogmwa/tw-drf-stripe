from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint, F
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.signals import request_finished

from api.models import Solution


class SolutionReview(models.Model):
    RATING_RANGE = range(1, 11)  # 1 to 10 (11 excluded)
    RATING_CHOICES = tuple(zip(RATING_RANGE, map(str, RATING_RANGE)))

    solution = models.ForeignKey(
        Solution, related_name='reviews', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='solution_reviews',
        # SET_NULL because we want to retain a review even if the corresponding user is deleted
        on_delete=models.SET_NULL,
    )
    content = models.TextField(max_length=1024, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}: {}".format(self.solution, self.user, self.rating)

    class Meta:
        # One user should not be able to vote on the same solution/web-service more than once
        constraints = [
            UniqueConstraint(fields=['solution', 'user'], name='user_solution_review')
        ]

        verbose_name = 'Solution Review'
        verbose_name_plural = 'Solution Reviews'


@receiver(pre_save, sender=SolutionReview)
def avg_rating_and_count_update_for_new_review(sender, instance=None, **kwargs):
    """
    When new review is added, the average rating of the solution is recalculated & 'avg_rating' and 'reviews_count'
    for the solution is updated
    """

    if type(sender) != type(SolutionReview):
        return

    try:
        # Update operation (an existing review is being updated case)
        # Try to get an old reference to this instance.
        instance_old = sender.objects.get(pk=instance.pk)
        if instance_old.rating != instance.rating:
            Solution.objects.filter(id=instance.solution_id).update(
                avg_rating=(
                    F('avg_rating') * F('reviews_count')
                    - instance_old.rating
                    + instance.rating
                )
                / (F('reviews_count')),
                reviews_count=F('reviews_count'),
            )

    except sender.DoesNotExist:
        # New review is being added
        Solution.objects.filter(id=instance.solution_id).update(
            avg_rating=(F('avg_rating') * F('reviews_count') + instance.rating)
            / (F('reviews_count') + 1),
            reviews_count=F('reviews_count') + 1,
        )


@receiver(post_delete, sender=SolutionReview)
def avg_rating_and_count_update_on_delete(sender, instance=None, **kwargs):
    solution_qs = Solution.objects.filter(id=instance.solution_qs)
    if solution_qs[0].reviews_count == 1:
        solution_qs.update(
            avg_rating=0,
            reviews_count=0,
        )
    else:
        solution_qs.update(
            avg_rating=(F('avg_rating') * F('reviews_count') - instance.rating)
            / (F('reviews_count') - 1),
            reviews_count=F('reviews_count') - 1,
        )


# https://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave
request_finished.connect(
    avg_rating_and_count_update_for_new_review,
    dispatch_uid="avg_rating_and_count_update_for_new_review",
)
