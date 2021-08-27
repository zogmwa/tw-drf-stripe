from django_elasticsearch_dsl.search import Search


def extract_results_from_matching_query(es_search: Search, case='tag') -> list:
    """From a matching es_search_query extract relevant results"""
    results = set()
    max_unique_items = 7

    # In the rare case of deleting and re-adding objects, there can be a scenario where the same item occurs
    # more than once in the index, we want to ensure response has unique results.
    max_processed_items = 10
    for i, hit in enumerate(es_search):
        if len(results) > max_unique_items or i >= max_processed_items:
            break
        else:
            # We are using the tag slug for suggestions for tags and name for assets
            if case == 'tag':
                results.add(hit.slug)
            else:
                results.add(hit.name)
    return list(results)
