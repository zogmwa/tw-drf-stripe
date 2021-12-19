"""
Allows Making sitemap.xml file from assets and solutions.
"""
from django.core.management.base import BaseCommand

import codecs
import datetime
from django.core.files.storage import default_storage
from gzip import GzipFile
import gzip
from django.conf import settings

from api.models.solution import Solution
from api.models.asset import Asset
from api.models.tag import Tag


def process() -> None:
    """
    Output sitemap urls to given sitemap.xml location.
    """
    print(datetime.datetime.now())
    max_url_per_sitemap = (
        50000  # maximum url of each sitemap - google recommended it should be 50K.
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
    current_output_filename = './static/sitemap_{}.xml.gz'.format(
        sitemap_file_index
    )  # First file created.
    sitemap_index_url.add('sitemap_{}.xml.gz'.format(sitemap_file_index))
    current_gzip_file = GzipFile(current_output_filename, 'w')
    # Write sitemap file content.
    current_gzip_file.write(sitemap_config_str.encode())
    # Write homepage and software list page url to sitemap.
    write_xml_str = """
<url><loc>https://www.taggedweb.com/</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>
<url><loc>https://www.taggedweb.com/softwares</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>
<url><loc>https://www.taggedweb.com/solutions</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>""".format(
        datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    current_gzip_file.write(write_xml_str.encode())
    current_url_count = current_url_count + 2

    # Write software list pages' url to sitemap.
    for chunk_tags in Tag.objects.values('slug').iterator(chunk_size=100):
        write_xml_str = """
<url><loc>https://www.taggedweb.com/softwares/{}</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>""".format(
            chunk_tags['slug'], datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        current_gzip_file.write(write_xml_str.encode())
        current_url_count = current_url_count + 1

        # if current urls count is 50K we should create a new sitemap file.
        if current_url_count == max_url_per_sitemap:
            current_gzip_file.write(sitemap_end_str.encode())
            current_gzip_file.close()
            current_url_count = 0
            sitemap_file_index = sitemap_file_index + 1
            current_output_filename = './static/sitemap_{}.xml.gz'.format(
                sitemap_file_index
            )
            current_gzip_file = GzipFile(current_output_filename, 'w')
            sitemap_index_url.add('sitemap_{}.xml.gz'.format(sitemap_file_index))
            current_gzip_file.write(sitemap_config_str.encode())

    for chunk_solutions in Solution.objects.values('slug').iterator(chunk_size=100):
        write_xml_str = """
<url><loc>https://www.taggedweb.com/solution/{}</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>""".format(
            chunk_solutions['slug'],
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        current_gzip_file.write(write_xml_str.encode())
        current_url_count = current_url_count + 1

        # if current urls count is 50K we should create a new sitemap file.
        if current_url_count == max_url_per_sitemap:
            current_gzip_file.write(sitemap_end_str.encode())
            current_gzip_file.close()
            current_url_count = 0
            sitemap_file_index = sitemap_file_index + 1
            current_output_filename = './static/sitemap_{}.xml.gz'.format(
                sitemap_file_index
            )
            current_gzip_file = GzipFile(current_output_filename, 'w')
            sitemap_index_url.add('sitemap_{}.xml.gz'.format(sitemap_file_index))
            current_gzip_file.write(sitemap_config_str.encode())

    current_gzip_file.write(sitemap_end_str.encode())
    current_gzip_file.close()
    current_url_count = 0
    sitemap_file_index = sitemap_file_index + 1
    current_output_filename = './static/sitemap_{}.xml.gz'.format(sitemap_file_index)
    current_gzip_file = GzipFile(current_output_filename, 'w')
    sitemap_index_url.add('sitemap_{}.xml.gz'.format(sitemap_file_index))
    current_gzip_file.write(sitemap_config_str.encode())

    # Create software compare pages' url in sitemap
    for chunk_softwares1 in Asset.objects.all().iterator(chunk_size=100):
        chunk_softwares1_tags = set(
            chunk_softwares1.tags.values_list('slug', flat=True)
        )
        for chunk_softwares2 in Asset.objects.all().iterator(chunk_size=100):
            if chunk_softwares1.slug >= chunk_softwares2.slug:
                continue
            chunk_softwares2_tags = set(
                chunk_softwares2.tags.values_list('slug', flat=True)
            )

            # check if two list has common element
            if chunk_softwares1_tags & chunk_softwares2_tags:
                current_url_count = current_url_count + 1
                write_xml_str = """
<url><loc>https://www.taggedweb.com/compare/{}-vs-{}</loc><changefreq>weekly</changefreq><priority>0.7</priority><lastmod>{}</lastmod></url>""".format(
                    chunk_softwares1.slug,
                    chunk_softwares2.slug,
                    datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
                current_gzip_file.write(write_xml_str.encode())
                # if current urls count is 50K we should create a new sitemap file.
                if current_url_count == max_url_per_sitemap:
                    current_gzip_file.write(sitemap_end_str.encode())
                    current_gzip_file.close()
                    current_url_count = 0
                    sitemap_file_index = sitemap_file_index + 1
                    current_output_filename = './static/sitemap_{}.xml.gz'.format(
                        sitemap_file_index
                    )
                    current_gzip_file = GzipFile(current_output_filename, 'w')
                    sitemap_index_url.add(
                        'sitemap_{}.xml.gz'.format(sitemap_file_index)
                    )
                    current_gzip_file.write(sitemap_config_str.encode())

    current_gzip_file.write(sitemap_end_str.encode())
    current_gzip_file.close()

    # Create sitemap index file content.
    sitemap_index_content = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""
    # Upload sitemap files to S3.
    for url in sitemap_index_url:
        sitemap_index_content += """
<sitemap>
    <loc>{}{}</loc>
    <lastmod>{}</lastmod>
</sitemap>""".format(
            settings.STATIC_URL,
            url,
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        file = default_storage.open(url, 'w')
        split_file = gzip.open('./static/{}'.format(url), 'rb')
        split_content = split_file.read()
        file.write(gzip.compress(split_content))
        file.close()

    current_gzip_file = codecs.open('./static/sitemap.xml', 'w', 'utf-8')

    sitemap_index_content += """
</sitemapindex>
"""
    current_gzip_file.write(sitemap_index_content)
    # Upload sitemap index file to S3.
    file = default_storage.open('sitemap.xml', 'w')
    file.write(sitemap_index_content.encode('utf-8'))
    file.close()

    print(datetime.datetime.now())


class Command(BaseCommand):
    def handle(self, **options):
        process()
