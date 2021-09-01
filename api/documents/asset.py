from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from api.documents.common import html_strip
from api.models import Asset, Tag


@registry.register_document
class AssetDocument(Document):
    """
    Web Asset Elasticsearch Document
    """

    short_description = fields.TextField(
        analyzer=html_strip, fields={'raw': fields.KeywordField()}
    )

    description = fields.TextField(
        analyzer=html_strip, fields={'raw': fields.KeywordField()}
    )

    tags = fields.NestedField(
        include_in_root=True,
        properties={
            'slug': fields.TextField(
                analyzer=html_strip,
                fields={'raw': fields.KeywordField()},
            ),
        },
    )

    class Index:
        # Name of the Elasticsearch index
        name = 'asset'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Asset
        related_models = [Tag]
        # The fields of the model you want to be indexed in Elasticsearch,
        # other than the ones already used in the Document class
        fields = [
            'slug',
            'name',
        ]

        # Ignore auto updating of Elasticsearch when a model is saved or deleted.
        ignore_signals = False

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000

    def get_queryset(self):
        return (
            super(AssetDocument, self)
            .get_queryset()
            .prefetch_related('tags', 'attributes')
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Asset):
            return related_instance.tags.all()