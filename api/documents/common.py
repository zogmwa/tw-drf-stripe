# ElasticSearch Documents
# https://django-elasticsearch-dsl.readthedocs.io/en/latest/quickstart.html#declare-data-to-index

from elasticsearch_dsl import analyzer

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)
