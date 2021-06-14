import pandas as pd
from django.core.management import BaseCommand
from django.utils.text import slugify
from furl import furl

from api.models import Tag, Asset


def process(tag_name: str, excel_path: str) -> None:
    df = pd.read_excel(excel_path)
    tag, is_created = Tag.objects.get_or_create(name=tag_name, slug=slugify(tag_name))

    for i, row in df.iterrows():
        name = row['Name'].strip()
        slug = slugify(name)
        website = row['Website'].strip()
        description = row['Description'].strip()
        asset, is_created = Asset.objects.get_or_create(slug=slug, name=name)
        asset.website = website
        asset.description = description
        furled_url = furl(website)
        asset.logo_url = 'https://logo.clearbit.com/{}'.format(furled_url.netloc)
        asset.tags.set([tag])
        asset.save()


class Command(BaseCommand):
    def handle(self, **options):
        default_excel_path = "../data/web-services.xlsx"
        excel_filepath = input("Enter XLS/XLSX relative path or leave blank for default ({}):\n".format(
            default_excel_path)
        ) or default_excel_path

        tag_name = input("Enter a tag name:\n")
        process(tag_name, excel_filepath)
