# ElasticSearch Documents
# https://django-elasticsearch-dsl.readthedocs.io/en/latest/quickstart.html#declare-data-to-index

from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer

from api.models import Tag

# The name of your index
tag = Index('tag')

# See Elasticsearch Indices API reference for available settings
tag.settings(
    number_of_shards=1,
    number_of_replicas=0
)

# html_strip = analyzer(
#     'html_strip',
#     tokenizer="standard",
#     filter=["standard", "lowercase", "stop", "snowball"],
#     char_filter=["html_strip"]
# )


@registry.register_document
@tag.document
class TagDocument(Document):
    """
    Tag Elasticsearch document
    """
    slug = fields.SearchAsYouTypeField()

    class Django:
        model = Tag
        # The fields of the model you want to be indexed in Elasticsearch,
        # other than the ones already used in the Document class
        fields = []

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000
