from django.core.management.base import BaseCommand

from api.models import Tag, Asset, LinkedTag


def _merge_tags(t1, t2):
    """
    Replace bad tag t1 with good tag t2.
    """
    bad_tag = Tag.objects.get(name=t1)
    good_tag = Tag.objects.get(name=t2)
    linked_tags_qs = LinkedTag.objects.filter(tag=bad_tag)
    linked_tags_qs.update(tag=good_tag)
    bad_tag.delete()


class Command(BaseCommand):
    help = 'Helps Merge Replace 2 tags (Replaces bad tag t1 with good tag t2). Updates M2M relationships.'

    def add_arguments(self, parser):
        parser.add_argument('--t1', type=str, help="The bad tag")
        parser.add_argument('--t2', type=str, help="The good tag")

    def handle(self, *args, **kwargs):
        t1, t2 = kwargs['t1'], kwargs['t2']
        _merge_tags(t1, t2)
