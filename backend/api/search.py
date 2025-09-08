"""Search utilities for the OpenWords backend.

This module provides a :func:`hybrid_search` function which performs a text
based search using OpenSearch and a vector based search using Qdrant.  The
two result sets are merged and ranked before being returned to the caller.

Connections are created lazily and are configured using the environment
variables ``OPENSEARCH_URL`` and ``QDRANT_URL``.  Sensible defaults are
provided so that the service continues to function in a local development
environment without any configuration.
"""

from os import getenv
from typing import Any, Dict, List

from opensearchpy import OpenSearch
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

OPENSEARCH_URL = getenv("OPENSEARCH_URL", "http://localhost:9200")
QDRANT_URL = getenv("QDRANT_URL", "http://localhost:6333")

_opensearch_client: OpenSearch | None = None
_qdrant_client: QdrantClient | None = None


def _get_opensearch() -> OpenSearch:
    """Return a cached OpenSearch client instance."""

    global _opensearch_client
    if _opensearch_client is None:
        _opensearch_client = OpenSearch(OPENSEARCH_URL, timeout=30)
    return _opensearch_client


def _get_qdrant() -> QdrantClient:
    """Return a cached Qdrant client instance."""

    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url=QDRANT_URL)
    return _qdrant_client


def _format_os_result(hit: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an OpenSearch hit into the API response schema."""

    source = hit.get("_source", {})
    return {
        "media_id": source.get("media_id", hit.get("_id")),
        "t0": source.get("t0"),
        "t1": source.get("t1"),
        "text": source.get("text"),
        "score": hit.get("_score", 0.0),
        "source": "opensearch",
    }


def _format_qdrant_result(point: qmodels.ScoredPoint) -> Dict[str, Any]:
    """Convert a Qdrant scored point into the API response schema."""

    payload = point.payload or {}
    return {
        "media_id": payload.get("media_id", point.id),
        "t0": payload.get("t0"),
        "t1": payload.get("t1"),
        "text": payload.get("text"),
        "score": point.score,
        "source": "qdrant",
    }


def hybrid_search(query: str, k: int = 20) -> Dict[str, Any]:
    """Perform a hybrid search across OpenSearch and Qdrant.

    Parameters
    ----------
    query:
        The textual query to search for.
    k:
        The maximum number of results to return.
    """

    os_client = _get_opensearch()
    qd_client = _get_qdrant()

    # ------------------------------------------------------------------
    # OpenSearch text search
    # ------------------------------------------------------------------
    os_hits: List[Dict[str, Any]] = []
    try:
        os_response = os_client.search(
            index="segments",
            body={
                "size": k,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["text"],
                        "fuzziness": "AUTO",
                    }
                },
            },
        )
        os_hits = [
            _format_os_result(hit)
            for hit in os_response.get("hits", {}).get("hits", [])
        ]
    except Exception:
        # If OpenSearch is unreachable or errors we return no results from it.
        os_hits = []

    # ------------------------------------------------------------------
    # Qdrant vector search
    # ------------------------------------------------------------------
    qd_hits: List[Dict[str, Any]] = []
    try:
        qd_response = qd_client.search(
            collection_name="segments",
            query_text=query,
            limit=k,
            with_payload=True,
        )
        qd_hits = [_format_qdrant_result(point) for point in qd_response]
    except Exception:
        qd_hits = []

    # Merge and rank results by score
    merged = sorted(os_hits + qd_hits, key=lambda r: r.get("score", 0.0), reverse=True)

    return {"query": query, "results": merged[:k]}

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
