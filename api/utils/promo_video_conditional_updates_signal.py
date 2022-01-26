from api.utils.video import get_embed_video_url


def promo_video_conditional_updates(sender, instance=None, **kwargs):
    """
    Performs some checks to compare old model state with new model state and perform conditional field update logic.
    Conditional updates help because they reduce average write time when saving many objects.
    """

    try:
        instance_old = sender.objects.get(pk=instance.pk)
        if instance.promo_video and instance_old.promo_video is None:
            # Only update the promo video if old video link was not set and the new is set
            instance.promo_video = get_embed_video_url(instance.promo_video)
    except sender.DoesNotExist:
        # If it's a new solution being created for which an old one does not exist then
        # we still want to update the promo video
        instance.promo_video = get_embed_video_url(instance.promo_video)
