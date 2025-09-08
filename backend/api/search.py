import os

def hybrid_search(query: str, k: int = 20):
    # TODO: connect to OpenSearch/Qdrant and return real results
    # For now, return a stubbed response structure.
    return {
        "query": query,
        "results": [
            {"media_id": "demo", "t0": 12.34, "t1": 18.9, "text": "Example snippet matching: " + query}
        ][:k]
    }