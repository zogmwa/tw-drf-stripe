"""
Allows making software list sitemap files from assets.
"""
from django.core.management.base import BaseCommand


from django.core.files.storage import default_storage
from gzip import GzipFile
import gzip

from api.models.asset import Asset
from api.utils.convert_str_to_date import get_now_converted_google_date


def process() -> None:
    print(get_now_converted_google_date())
    sitemap_index_name = 'software_detail'
    max_url_per_sitemap = (
        500  # maximum url of each sitemap - google recommended it should be 50K.
    )
    sitemap_name_index = 0  # index of each sitemap file name
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
    current_output_filename = './static/sitemap_{}_{}.xml.gz'.format(
        sitemap_index_name, sitemap_file_index
    )  # First file created.
    sitemap_index_url.add(
        'sitemap_{}_{}.xml.gz'.format(sitemap_index_name, sitemap_file_index)
    )
    current_gzip_file = GzipFile(current_output_filename, 'w')
    # Write sitemap file content.
    current_gzip_file.write(sitemap_config_str.encode())
    # Write homepage and software list page url to sitemap.
    write_xml_str = """
<url><loc>https://www.taggedweb.com/</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>
<url><loc>https://www.taggedweb.com/softwares</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>
<url><loc>https://www.taggedweb.com/solutions</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>""".format(
        get_now_converted_google_date(),
        get_now_converted_google_date(),
        get_now_converted_google_date(),
    )
    current_gzip_file.write(write_xml_str.encode())
    current_url_count = current_url_count + 2

    # Write software list pages' url to sitemap.
    for chunk_software in Asset.objects.all().iterator(chunk_size=100):
        write_xml_str = """
        <url><loc>https://www.taggedweb.com/softwares/{}</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>""".format(
            chunk_software.slug, get_now_converted_google_date()
        )
        current_gzip_file.write(write_xml_str.encode())
        current_url_count = current_url_count + 1

        # if current urls count is 500 we should create a new sitemap file.
        if current_url_count == max_url_per_sitemap:
            current_gzip_file.write(sitemap_end_str.encode())
            current_gzip_file.close()
            current_url_count = 0
            sitemap_file_index = sitemap_file_index + 1
            current_output_filename = './static/sitemap_{}_{}.xml.gz'.format(
                sitemap_index_name, sitemap_file_index
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
        split_file = gzip.open('./static/{}'.format(url), 'rb')
        split_content = split_file.read()
        file.write(gzip.compress(split_content))
        file.close()

    print(get_now_converted_google_date())


class Command(BaseCommand):
    def handle(self, **options):
        process()
