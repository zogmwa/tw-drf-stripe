import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from guardian.mixins import GuardianUserMixin


def _upload_to_for_avatars(instance, filename):
    path = "images/avatars/"
    filename_with_extension = "{}.{}".format(
        instance.username, instance.avatar.file.image.format.lower()
    )
    return os.path.join(path, filename_with_extension)


class User(AbstractUser, GuardianUserMixin):
    """
    This is a TaggedWeb user, a user can be an administrator someone else who wants to submit their web asset
    for listing on TaggedWeb. A user can also be an application like our frontend application using our API token
    to fetch details about a web asset.
    """

    api_daily_rate_limit = models.IntegerField(default=2000)
    avatar = models.ImageField(null=True, blank=True, upload_to='images/avatars/')

    def __str__(self):
        return '{}'.format(
            self.username,
        )

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
