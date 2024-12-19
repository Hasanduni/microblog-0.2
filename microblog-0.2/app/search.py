from flask import current_app

def add_to_index(index, model):
    """Adds a document to the Elasticsearch index."""
    if not current_app.elasticsearch:
        return
    payload = {field: getattr(model, field) for field in model.__searchable__}
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)

def remove_from_index(index, model):
    """Removes a document from the Elasticsearch index."""
    if not current_app.elasticsearch:
        return
    try:
        current_app.elasticsearch.delete(index=index, id=model.id)
    except Exception as e:
        # Log or handle exceptions (e.g., document not found)
        current_app.logger.error(f"Error removing document from index: {e}")

from elasticsearch.exceptions import ConnectionError

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    try:
        search = current_app.elasticsearch.search(
            index=index,
            body={
                'query': {'multi_match': {'query': query, 'fields': ['*']}},
                'from': (page - 1) * per_page,
                'size': per_page
            }
        )
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        total = search['hits']['total']['value']
        return ids, total
    except ConnectionError as e:
        current_app.logger.error(f"Connection error: {e}")
        return [], 0
    except Exception as e:
        current_app.logger.error(f"Error querying Elasticsearch: {e}")
        return [], 0
