from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint, F
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.core.signals import request_finished

from api.models import Solution


class SolutionReview(models.Model):
    class Type(models.TextChoices):
        SAD = 'S'
        NEUTRAL = 'N'
        HAPPY = 'H'

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

    type = models.CharField(max_length=2, choices=Type.choices)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}: {}".format(self.solution, self.user, self.type)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['solution', 'user', 'type'], name='user_solution_review'
            )
        ]
        verbose_name = 'Solution Review'
        verbose_name_plural = 'Solution Reviews'


def decrease_status_count_of_solution(solution_review):
    """
    Decreasing solution's status count of solution revivew instance
    """
    solution_id = solution_review.solution_id
    if solution_review.type == SolutionReview.Type.SAD:
        Solution.objects.filter(id=solution_id).update(sad_count=F('sad_count') - 1)
    elif solution_review.type == SolutionReview.Type.NEUTRAL:
        Solution.objects.filter(id=solution_id).update(
            neutral_count=F('neutral_count') - 1
        )
    elif solution_review.type == SolutionReview.Type.HAPPY:
        Solution.objects.filter(id=solution_id).update(happy_count=F('happy_count') - 1)


def increase_status_count_of_solution(solution_review):
    """
    Increasing solution's status count of solution revivew instance
    """
    solution_id = solution_review.solution_id
    if solution_review.type == SolutionReview.Type.SAD:
        Solution.objects.filter(id=solution_id).update(sad_count=F('sad_count') + 1)
    elif solution_review.type == SolutionReview.Type.NEUTRAL:
        Solution.objects.filter(id=solution_id).update(
            neutral_count=F('neutral_count') + 1
        )
    elif solution_review.type == SolutionReview.Type.HAPPY:
        Solution.objects.filter(id=solution_id).update(happy_count=F('happy_count') + 1)


@receiver(pre_save, sender=SolutionReview)
def status_count_update_for_solution_review(sender, instance=None, **kwargs):
    """
    When a new solution review is added, the status count of solution is recalculated and updated.
    """
    if type(sender) != type(SolutionReview):
        return

    try:
        old_instance = sender.objects.get(
            solution=instance.solution, user=instance.user
        )
        if old_instance:
            # When a old solution review is being updated.
            if instance.type != old_instance.type:
                """
                If new solution review type is different from old one,
                then old status type count should be decreased
                and new status type count should be increased in solution.
                """
                decrease_status_count_of_solution(old_instance)
                increase_status_count_of_solution(instance)
        else:
            # When a new solution review is being added, status type count in solution is increased.
            increase_status_count_of_solution(instance)

    except sender.DoesNotExist:
        # New solution review is being added
        increase_status_count_of_solution(instance)


@receiver(post_delete, sender=SolutionReview)
def decrease_status_type_count_of_solution(sender, instance=None, **kwargs):
    if type(sender) != type(SolutionReview):
        return

    decrease_status_count_of_solution(instance)


# https://code.djangoproject.com/wiki/Signals#Helppost_saveseemstobeemittedtwiceforeachsave
request_finished.connect(
    status_count_update_for_solution_review,
    dispatch_uid="status_count_update_for_solution_review",
)
