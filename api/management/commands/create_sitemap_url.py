"""
Allows Making sitemap.xml file from assets and solutions.
"""
from django.core.management.base import BaseCommand

from io import BytesIO
import xml.etree.ElementTree as ET
from xml.dom import minidom

from api.models.solution import Solution
from api.models.asset import Asset
import datetime


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

    solutions = Solution.objects.all()
    softwares = Asset.objects.all()

    solution_slugs = [solution.slug for solution in solutions]
    software_slugs = [software.slug for software in softwares]

    for solution in solution_slugs:
        generated_url.add('https://www.taggedweb.com/solution/' + solution + '/')

    for software in software_slugs:
        generated_url.add('https://www.taggedweb.com/software/' + software + '/')

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
        default_sitemap_path = "../data/sitemap.xml"
        sitemap_path = (
            input(
                "Enter CSV relative path or leave blank for default ({}):\n".format(
                    default_sitemap_path
                )
            )
            or default_sitemap_path
        )

        process(sitemap_path)
