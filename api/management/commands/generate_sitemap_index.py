"""
Allows making sitemap index file that from sitemap files in ./static folder.
"""
from django.core.management.base import BaseCommand
from os import listdir
from os.path import isfile, join
import codecs

from django.core.files.storage import default_storage
from api.utils.convert_str_to_date import get_now_converted_google_date


def process() -> None:
    print(get_now_converted_google_date())
    sitemap_files = [
        file for file in listdir('./static/') if isfile(join('./static/', file))
    ]
    sitemap_files.remove('sitemap.xml')

    sitemap_index_content = """<?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""
    # Upload sitemap files to S3.
    for url in sitemap_files:
        sitemap_index_content += """
    <sitemap>
        <loc>https://www.taggedweb.com/{}</loc>
        <lastmod>{}</lastmod>
    </sitemap>""".format(
            url,
            get_now_converted_google_date(),
        )
    sitemap_index_file = codecs.open('./static/sitemap.xml', 'w', 'utf-8')
    sitemap_index_content += """
    </sitemapindex>
    """
    sitemap_index_file.write(sitemap_index_content)

    # Upload sitemap index file to S3.
    file = default_storage.open('sitemap.xml', 'w')
    file.write(sitemap_index_content.encode('utf-8'))
    file.close()
    print(get_now_converted_google_date())


class Command(BaseCommand):
    def handle(self, **options):
        process()
