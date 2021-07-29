import logging

import pandas as pd
import ast
from django.core.management import BaseCommand
from django.db import IntegrityError
from django.utils.text import slugify
from furl import furl

from api.models import Tag, Asset


def _get_slug_name(tag_name: str) -> str:
    """ Get slug from the tag name """
    # This is the list of special tags in which the slugs are special
    SPECIAL_TAGS = {
        'Machine Learning (ML)': 'machine-learning',
        'Learning Management System (LMS)': 'lms',
        'Computer Algebra System (CAS)': 'cas',
        'Global Positioning System (GPS)': 'gps',
        'Customer Data Platform (CDP)': 'customer-data-platform',
        'Computer Aided Design (CAD)': 'cad',
        'Augmented Reality (AR)': 'ar',
        'Virtual Reality (VR)': 'virtual-reality',
        'Virtual Private Network (VPN)': 'vpn',
        'Enterprise Resource Planning (ERP)': 'erp',
        'Supply Chain Management (SCM)': 'supply-chain-management',
        'Search Engine Optimization (SEO)': 'seo',
        'Customer Relationship Management (CRM)': 'crm',
        'Corporate Social Responsibility (CSR)': 'corporate-social-responsibility',
        'Application Performance Monitoring (APM)': 'application-performance-monitoring',
        'Non Fungible Tokens (NFT)': 'nft',
        'Environmental Health and Safety': 'ehs',
        'Environmental, Social and Governance': 'esg',
        'User Experience Design (UXD)': 'ux-design',
        'Q&A': 'qna',
        'Accounts Payable (AP)': 'accounts-payable',
        'Voice over IP (VoIP)': 'voip',
    }

    # This is just for special tags
    if tag_name in SPECIAL_TAGS.keys():
        slug = SPECIAL_TAGS[tag_name]
    else:
        slug = slugify(tag_name)
    return slug


def process(excel_path: str) -> None:
    df = pd.read_excel(excel_path)

    for i, row in df.iterrows():
        name = row[Asset.name.field.attname].strip()
        slug = slugify(name)[:50]
        website = row[Asset.website.field.attname].strip()
        print(website)

        asset, is_created = Asset.objects.get_or_create(name=name)
        asset.slug = slug
        short_description_field_name = Asset.short_description.field.attname
        description_field_name = Asset.description.field.attname

        promo_video_field_name = Asset.promo_video.field.attname

        if row.get(short_description_field_name) and not pd.isnull(row[short_description_field_name]):
            asset.short_description = row[short_description_field_name].strip()

            if "_x000D_" in asset.short_description:
                # Replaces _X000D_ character in short description if there
                asset.short_description = asset.short_description.replace("_x000D_", "\n")

            if "x000D" in asset.short_description:
                # Replaces X000D character in short description if there
                asset.short_description = asset.short_description.replace("x000D", "\n")

        if row.get(description_field_name) and not pd.isnull(row[description_field_name]):
            asset.description = row[description_field_name].strip()

            if "_x000D_" in asset.description:
                # Replaces _X000D_ character in description if there
                asset.description = asset.description.replace("_x000D_", "\n")

            if "x000D" in asset.description:
                # Replaces X000D character in description if there
                asset.description = asset.description.replace("x000D", "\n")

        if row.get(promo_video_field_name) and not pd.isnull(row[promo_video_field_name]):
            asset.promo_video = row[promo_video_field_name].strip()

        asset.website = website
        asset.is_published = True

        furled_url = furl(website)
        asset.logo_url = 'https://logo.clearbit.com/{}'.format(furled_url.netloc)

        # Only set the tags if the tags column is provided in the input excel, else skip/keep existing tags
        tags_list_string = row.get('tags')
        if tags_list_string:
            tag_names = ast.literal_eval(tags_list_string)
            tags = set()

            for tag_name in tag_names:
                tag, is_created = Tag.objects.get_or_create(
                    name=tag_name,
                    slug=_get_slug_name(tag_name),
                )
                tags.add(tag)

            asset.tags.set(list(tags))

        asset.save()


class Command(BaseCommand):
    def handle(self, **options):
        default_excel_path = "../data/web-services.xlsx"
        excel_filepath = input("Enter XLS/XLSX relative path or leave blank for default ({}):\n".format(
            default_excel_path)
        ) or default_excel_path

        process(excel_filepath)
