"""
This command isn't tested yet. Use with caution. (Feel free to remove this caveat if you have tested it).
"""
import logging

import pandas as pd
import ast
from django.core.management import BaseCommand
from django.db import IntegrityError

from api.models import Asset, Organization, OrganizationUsingAsset


def process(excel_path: str, asset_slug: str) -> None:
    df = pd.read_excel(excel_path)

    for i, row in df.iterrows():
        # Assuming that the excel sheet columns are name, website, and logo_url
        name = row[Organization.name.field.attname].strip()
        logo_url = row.get(Organization.logo_url.field.attname)
        website = row.get(Organization.website.field.attname)

        organization, is_created = Organization.objects.get_or_create(
            name=name,
        )  # Create a new organization with the company name

        asset, is_created = Asset.objects.get_or_create(
            slug=asset_slug,
        )  # Find an asset with the asset slug

        if logo_url:
            organization.logo_url = row[Organization.logo_url.field.attname].strip()

        if website:
            organization.website = row[Organization.website.field.attname].strip()

        organization.save()

        OrganizationUsingAsset.objects.get_or_create(
            organization=organization, asset=asset
        )  # Create the company with the organization and the asset


class Command(BaseCommand):
    def handle(self, **options):
        default_excel_path = "../data/organizations.xlsx"  # Assuming that the excel sheet columns are name, website, and logo_url
        excel_filepath = (
            input(
                "Enter XLS/XLSX relative path or leave blank for default ({}):\n".format(
                    default_excel_path
                )
            )
            or default_excel_path
        )
        asset_slug = input("Enter the slug of your asset:\n")

        process(excel_filepath, asset_slug)
