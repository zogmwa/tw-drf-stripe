from api.management.commands.merge_tags import _merge_tags
from api.models import Tag, Asset


def test__merge_tags():
    tag1_obj = Tag.objects.create(name='t1', slug='t1')
    tag2_obj = Tag.objects.create(name='t2', slug='t2')
    asset = Asset.objects.create(
        slug='test-asset',
        name='Test Asset',
        website='example.com',
        short_description='Test',
        description='Test',
    )
    asset.tags.set([tag1_obj])
    asset.save()
    assert asset.tags.get() == tag1_obj

    _merge_tags(tag1_obj.name, tag2_obj.name)

    assert asset.tags.get() == tag2_obj
