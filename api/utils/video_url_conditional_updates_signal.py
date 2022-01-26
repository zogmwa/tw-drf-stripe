from api.utils.video import get_embed_video_url


def video_url_conditional_updates(sender, instance=None, **kwargs):
    """
    Performs some checks to compare old review model state with new review model state and perform conditional field
    update logic like updating video_url to an embed video url the first time the video url is being set.
    Conditional updates help because they reduce average write time when saving many objects.
    """
    try:
        instance_old = sender.objects.get(pk=instance.pk)
        if instance.video_url and instance_old.video_url is None:
            # Only update the promo video if old video link was not set and the new is set
            instance.video_url = get_embed_video_url(instance.video_url)
    except sender.DoesNotExist:
        # If it's a new asset/web-service being created for which an old one does not exist then
        # we still want to update the promo video
        instance.video_url = get_embed_video_url(instance.video_url)
