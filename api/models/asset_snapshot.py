from django.db import models
from api.models import Asset


class AssetSnapshot(models.Model):
    asset = models.ForeignKey(
        Asset,
        null=True,
        blank=True,
        related_name='snapshots',
        on_delete=models.CASCADE,
    )
    # A public URL for the snapshot (The snapshot is saved to Cloudinary from the frontend itself and added to
    # Cloudinary)
    url = models.URLField(blank=True, max_length=2048, null=True)

    # This will specify if this is the snapshot that will be featured on the home page
    is_featured = models.BooleanField(default=False)
