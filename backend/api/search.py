"""Search indexing and query stubs."""

import os
from typing import List, Dict


def index_transcript(media_id: str, transcript: List[Dict]) -> None:
    """Index a transcript into the search backends.

    This function is currently a placeholder. In a real implementation the
    segments would be sent to OpenSearch/Qdrant for hybrid search.

    Args:
        media_id: Unique identifier for the media.
        transcript: List of segment dictionaries produced by Whisper/WhisperX.
    """

    # TODO: Implement OpenSearch/Qdrant indexing logic here.
    _ = (media_id, transcript)  # pragma: no cover - placeholder


def hybrid_search(query: str, k: int = 20) -> Dict[str, List[Dict]]:
    """Perform a hybrid search over indexed transcripts.

    Args:
        query: Text to search for.
        k: Number of results to return.

    Returns:
        A stubbed response mimicking the structure of a real search result.
    """

    # TODO: connect to OpenSearch/Qdrant and return real results
    return {
        "query": query,
        "results": [
            {
                "media_id": "demo",
                "t0": 12.34,
                "t1": 18.9,
                "text": "Example snippet matching: " + query,
            }
        ][:k],
    }
