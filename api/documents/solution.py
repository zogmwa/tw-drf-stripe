from django_elasticsearch_dsl.documents import Document
from django_elasticsearch_dsl import fields, search
from django_elasticsearch_dsl.registries import registry

from api.documents.common import html_strip
from api.models import Solution, Tag


@registry.register_document
class SolutionDocument(Document):
    """
    Solution Elasticsearch Document
    """

    @classmethod
    def search(cls, using=None, index=None):
        """
        If we don't override this method and slice the search like this, the default search method will be used and
        that method does not return all the results calculated by elasticsearch. The default method returns default
        setting which may vary depending on the system and will return partial queryset
        reference:https://github.com/elastic/elasticsearch-dsl-py/issues/737
        """
        search = super().search(using, index)
        search = search[0 : search.count()]
        return search

    title = fields.TextField(analyzer=html_strip, fields={'raw': fields.KeywordField()})

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
        name = 'solution'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Solution
        related_models = [Tag]
        # The fields of the model you want to be indexed in Elasticsearch,
        # other than the ones already used in the Document class
        fields = []

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        ignore_signals = False

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000

    def get_queryset(self):
        return (
            super(SolutionDocument, self)
            .get_queryset()
            .prefetch_related('tags')
            .select_related('stripe_product', 'stripe_primary_price')
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Solution):
            return related_instance.tags.all()
