"""
Allows making software list sitemap files from tags.
"""
from django.core.management.base import BaseCommand


from django.core.files.storage import default_storage
from gzip import GzipFile
import gzip
import os
from django.conf import settings
from api.models.tag import Tag
from api.utils.convert_str_to_date import get_now_converted_google_date


def process() -> None:
    print(get_now_converted_google_date())
    sitemap_file_path = '{}{}'.format(settings.BASE_DIR, '/temp/')
    if os.path.isdir(sitemap_file_path) is False:
        os.mkdir(os.path.join(sitemap_file_path))

    sitemap_index_name = 'software_list'
    max_url_per_sitemap = (
        500  # maximum url of each sitemap - google recommended it should be 50K.
    )
    sitemap_file_index = 1  # each sitemap file index.
    current_url_count = 0  # url counter of each sitemap file
    sitemap_index_url = set()  # sitemap files' url saver.
    sitemap_config_str = """<?xml version="1.0" encoding="UTF-8" ?>
<urlset
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">"""
    sitemap_end_str = """
</urlset>
"""
    current_output_filename = '{}/sitemap_{}_{}.xml.gz'.format(
        sitemap_file_path, sitemap_index_name, sitemap_file_index
    )  # First file created.
    sitemap_index_url.add(
        'sitemap_{}_{}.xml.gz'.format(sitemap_index_name, sitemap_file_index)
    )
    current_gzip_file = GzipFile(current_output_filename, 'w')
    # Write sitemap file content.
    current_gzip_file.write(sitemap_config_str.encode())
    # Write software list index page url to sitemap.
    write_xml_str = """
    <url><loc>https://www.taggedweb.com/softwares</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>""".format(
        get_now_converted_google_date(),
    )
    current_gzip_file.write(write_xml_str.encode())
    current_url_count = current_url_count + 1

    # Write software list pages' url to sitemap.
    for chunk_tags in Tag.objects.values('slug').iterator(chunk_size=100):
        write_xml_str = """
    <url><loc>https://www.taggedweb.com/softwares/{}</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>""".format(
            chunk_tags['slug'], get_now_converted_google_date()
        )
        current_gzip_file.write(write_xml_str.encode())
        current_url_count = current_url_count + 1

        # if current urls count is 500 we should create a new sitemap file.
        if current_url_count == max_url_per_sitemap:
            current_gzip_file.write(sitemap_end_str.encode())
            current_gzip_file.close()
            current_url_count = 0
            sitemap_file_index = sitemap_file_index + 1
            current_output_filename = '{}/sitemap_{}_{}.xml.gz'.format(
                sitemap_file_path, sitemap_index_name, sitemap_file_index
            )
            current_gzip_file = GzipFile(current_output_filename, 'w')
            sitemap_index_url.add(
                'sitemap_{}_{}.xml.gz'.format(sitemap_index_name, sitemap_file_index)
            )
            current_gzip_file.write(sitemap_config_str.encode())

    current_gzip_file.write(sitemap_end_str.encode())
    current_gzip_file.close()

    # Upload sitemap files to S3.
    for url in sitemap_index_url:
        file = default_storage.open(url, 'w')
        split_file = gzip.open('{}{}'.format(sitemap_file_path, url), 'rb')
        split_content = split_file.read()
        file.write(gzip.compress(split_content))
        file.close()

    print(get_now_converted_google_date())


class Command(BaseCommand):
    def handle(self, **options):
        process()
