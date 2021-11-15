from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint, F
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from api.models import Solution


class SolutionVote(models.Model):
    # For now we will only have upvotes, no downvotes
    is_upvote = models.BooleanField(
        default=True, help_text='Whether this is an Upvote=true (or Downvote=false)'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='solution_votes',
        on_delete=models.CASCADE,
    )
    voted_on = models.DateTimeField(auto_now_add=True)
    solution = models.ForeignKey(
        Solution, related_name='solution_votes', on_delete=models.CASCADE
    )

    def __str__(self):
        return "{}: {}".format(self.solution, self.user)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['solution', 'user'], name='user_solution_vote')
        ]
        verbose_name = 'Solution Vote'
        verbose_name_plural = 'Solution Votes'


def _change_upvotes_count(solution_id: int, change_by: int) -> None:
    Solution.objects.filter(id=solution_id).update(
        upvotes_count=F('upvotes_count') + change_by
    )


@receiver(pre_save, sender=SolutionVote)
def update_solution_upvote_count_metric_for_new_vote(sender, instance=None, **kwargs):
    """
    if the is_upvote is false for the instance, upvotes_count will not change.
    But if it is true then:
    If the solution_upvote instance is already present in the database & instance_old.is_upvote is false or
    instance_old does not exist then the upvotes_count of an solution will increase by 1
    """
    if instance.is_upvote:
        try:
            # Try to get an old reference to this instance.
            instance_old = sender.objects.get(pk=instance.pk)
            if not instance_old.is_upvote:
                _change_upvotes_count(instance.solution_id, 1)

        except sender.DoesNotExist:
            _change_upvotes_count(instance.solution_id, 1)


@receiver(post_delete, sender=SolutionVote)
def update_solution_upvote_count_metric_when_vote_is_deleted(
    sender, instance=None, **kwargs
):
    if instance.is_upvote:
        _change_upvotes_count(instance.solution_id, -1)
