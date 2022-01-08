"""
Allows making all the sitemap files using generate sitemap file commands.
"""
from django.core.management.base import BaseCommand
from api.management.commands import generate_sitemap_solution_detail
from api.management.commands import generate_sitemap_software_detail
from api.management.commands import generate_sitemap_software_list
from api.management.commands import generate_sitemap_index
from api.utils.convert_str_to_date import get_now_converted_google_date


def process() -> None:
    print(get_now_converted_google_date())
    solution_detail_cmd = generate_sitemap_solution_detail.Command()
    software_list_cmd = generate_sitemap_software_list.Command()
    software_detail_cmd = generate_sitemap_software_detail.Command()
    sitemap_index_cmd = generate_sitemap_index.Command()
    solution_detail_cmd.handle(**{})
    software_list_cmd.handle(**{})
    software_detail_cmd.handle(**{})
    sitemap_index_cmd.handle(**{})
    print(get_now_converted_google_date())


class Command(BaseCommand):
    def handle(self, **options):
        process()
