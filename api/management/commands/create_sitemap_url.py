"""
Allows Making sitemap.xml file from assets and solutions.
"""
from django.core.management.base import BaseCommand

from io import BytesIO
import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime

from api.models.solution import Solution
from api.models.asset import Asset


def process(default_sitemap_path) -> None:
    """
    Output sitemap urls to given sitemap.xml location.
    """
    generated_url = set()
    data = ET.Element('urlset')
    data.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    data.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
    data.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
    data.set('xmlns:mobile', 'http://www.google.com/schemas/sitemap-mobile/1.0')
    data.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    data.set('xmlns:video', 'http://www.google.com/schemas/sitemap-video/1.1')

    generated_url.add('https://www.taggedweb.com/')
    generated_url.add('https://www.taggedweb.com/softwares/')

    for main_softwares_record in Asset.objects.all().iterator(chunk_size=3):
        for other_softwares_record in Asset.objects.all().iterator(chunk_size=3):
            generated_url.add(
                'https://www.taggedweb.com/'
                + main_softwares_record.slug
                + '-vs-'
                + other_softwares_record.slug
                + '/'
            )

    for chunk_solutions in Solution.objects.all().iterator(chunk_size=2):
        generated_url.add(
            'https://www.taggedweb.com/solution/' + chunk_solutions.slug + '/'
        )

    for url in generated_url:
        add_xml_data = ET.SubElement(data, 'url')
        sub_loc = ET.SubElement(add_xml_data, 'loc')
        sub_loc.text = url
        sub_changefreq = ET.SubElement(add_xml_data, 'changefreq')
        sub_changefreq.text = 'daily'
        sub_priority = ET.SubElement(add_xml_data, 'priority')
        sub_priority.text = '0.7'
        sub_lastmode = ET.SubElement(add_xml_data, 'lastmod')
        sub_lastmode.text = str(datetime.datetime.now())

    et = ET.ElementTree(data)
    f = BytesIO()
    et.write(f, encoding='utf-8')
    xml = f.getvalue()
    xmlstr = minidom.parseString(xml).toprettyxml(indent="   ")
    print(xmlstr)

    with open(default_sitemap_path, "wb") as f:
        f.write(xmlstr.encode('utf-8'))


class Command(BaseCommand):
    def handle(self, **options):
        default_sitemap_path = "./data/sitemap.xml"
        process(default_sitemap_path)
