"""
Allows loading assets from a CSV, should have a header column with name, description fields.
And optionally logo_url, website fields.
"""
from django.core.management.base import BaseCommand
import csv

from django.utils.text import slugify

from api.models import Tag, Asset


def process(tag_name: str, csv_filepath: str) -> None:
    """
    Name of the tag applied to all entities in this asset list. Note only entities having the
    same tag should be processed at once.
    """
    tag, is_created = Tag.objects.get_or_create(name=tag_name, slug=slugify(tag_name))

    with open(csv_filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            asset_name = row[Asset.name.field.attname].strip()

            logo_url = row.get(Asset.logo_url.field.attname)
            website = row.get(Asset.website.field.attname)

            asset, is_created = Asset.objects.get_or_create(
                slug=slugify(asset_name),
                name=asset_name,
            )

            asset.description = row[Asset.description.field.attname].strip()

            if logo_url:
                asset.logo_url = logo_url.strip()

            if website:
                asset.website = website.strip()

            asset.is_published = True
            asset.save()
            asset.tags.set([tag])


class Command(BaseCommand):
    def handle(self, **options):
        default_csv_path = "../data/web-assets-list.csv"
        csv_filepath = (
            input(
                "Enter CSV relative path or leave blank for default ({}):\n".format(
                    default_csv_path
                )
            )
            or default_csv_path
        )

        tag_name = input("Enter a tag name:\n")
        process(tag_name, csv_filepath)
