from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint, F
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from api.models import AssetQuestion


class AssetQuestionVote(models.Model):
    """
    A vote on a specific Question/Answer on a specific asset (only one vote per user per Answer per asset).
    """

    is_upvote = models.BooleanField(
        default=True, help_text='Whether this is helpful (or Downvote= not relevant)'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='asset_question_votes',
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        AssetQuestion, related_name='votes', on_delete=models.CASCADE
    )

    voted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}: {}".format(self.question, self.user)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'question'],
                name='user_asset_question_vote',
            )
        ]
        verbose_name = 'Question Vote'
        verbose_name_plural = 'Question Votes'


def _change_question_upvotes_count(question_id: int, change_by: int) -> None:
    asset_question_qs = AssetQuestion.objects.filter(id=question_id)
    asset_question_qs.update(upvotes_count=F('upvotes_count') + change_by)


@receiver(pre_save, sender=AssetQuestionVote)
def update_asset_upvote_count_metric_for_new_vote(sender, instance=None, **kwargs):
    """
    if the is_upvote is false for the instance, upvotes_count will not change.
    But if it is true then:
    If the asset_upvote instance is already present in the database & instance_old.is_upvote is false or
    instance_old does not exist then the upvotes_count of an asset will increase by 1
    """
    if instance.is_upvote:
        try:
            # Try to get an old reference to this instance.
            instance_old = sender.objects.get(pk=instance.pk)
            if not instance_old.is_upvote:
                _change_question_upvotes_count(instance.question.id, 1)

        except sender.DoesNotExist:
            _change_question_upvotes_count(instance.question.id, 1)


@receiver(post_delete, sender=AssetQuestionVote)
def update_asset_upvote_count_metric_when_vote_is_deleted(
    sender, instance=None, **kwargs
):
    if instance.is_upvote:
        _change_question_upvotes_count(instance.question.id, -1)
