from django_elasticsearch_dsl.documents import Document
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from api.models import Tag


@registry.register_document
class TagDocument(Document):
    """
    Tag Elasticsearch Document
    """

    name = fields.SearchAsYouTypeField()

    class Index:
        # Name of the Elasticsearch index
        name = 'tag'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Tag
        # The fields of the model you want to be indexed in Elasticsearch,
        # other than the ones already used in the Document class
        fields = ['slug']

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000
