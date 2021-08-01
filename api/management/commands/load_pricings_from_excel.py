import json
import logging

import pandas as pd
from django.core.management import BaseCommand
from django.db import IntegrityError

from api.models import Asset, PricePlan


def process(excel_path: str) -> None:
    df = pd.read_excel(excel_path)

    for i, row in df.iterrows():
        asset_slug = row['asset_slug'].strip()  # The col with the asset slugs is 'asset_slug' just for specifics
        asset, is_created = Asset.objects.get_or_create(slug=asset_slug)

        asset_pricings = json.loads(row['pricing_data'])  # The pricing data is in the form of a dictionary

        if asset_slug in asset_pricings.keys():
            asset_plans = asset_pricings[asset_slug]
            for plan_name in asset_plans.keys():
                price_plan, is_created = PricePlan.objects.get_or_create(asset=asset.id, name=plan_name) #Instead of an asset, we take the id of the asset model
                plan_price_field_name = PricePlan.price.field.attname
                plan_per_field_name = PricePlan.per.field.attname
                plan_features_field_name = PricePlan.features.field.attname
                plan_currency_field_name = PricePlan.currency.field.attname
                plan_summary_field_name = PricePlan.summary.field.attname
                price_plan.plan_price = asset_plans[plan_name][plan_price_field_name].strip()
                price_plan.plan_per = asset_plans[plan_name][plan_per_field_name].strip()

                if plan_summary_field_name in asset_plans[plan_name].keys():
                    price_plan.features = asset_plans[plan_name][plan_summary_field_name].strip()

                if plan_features_field_name in asset_plans[plan_name].keys():
                    price_plan.features = asset_plans[plan_name][plan_features_field_name].strip()

                if plan_currency_field_name in asset_plans[plan_name].keys():
                    price_plan.currency = asset_plans[plan_name][plan_currency_field_name].strip()

                price_plan.save()


class Command(BaseCommand):
    def handle(self, **options):
        default_excel_path = "../data/pricings.xlsx"
        excel_filepath = input("Enter XLS/XLSX relative path for pricings or leave blank for default ({}):\n".format(
            default_excel_path)
        ) or default_excel_path

        process(excel_filepath)
