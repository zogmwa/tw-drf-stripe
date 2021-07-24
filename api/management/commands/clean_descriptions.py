from django.core.management import BaseCommand

from api.models import Asset


def clean_asset_descriptions() -> None:
    asset_list = Asset.objects.all()
    batch = []

    for asset in asset_list:
        if asset.description is not None:
            if "_x000D_" in asset.description:
                asset.description = asset.description.replace("_x000D_", "\n")

            if "x000D" in asset.description:
                asset.description = asset.description.replace("x000D", "\n")

        if asset.short_description is not None:
            if "_x000D_" in asset.short_description:
                asset.short_description = asset.short_description.replace("_x000D_", "\n")

            if "x000D" in asset.short_description:
                asset.short_description = asset.short_description.replace("x000D", "\n")

        batch.append(asset)

        if len(batch) == 500:
            Asset.objects.bulk_update(batch, ['description', 'short_description'])
            batch = []

    Asset.objects.bulk_update(batch, ['description', 'short_description'])


class Command(BaseCommand):
    def handle(self, **options):
        clean_asset_descriptions()
