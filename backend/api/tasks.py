import os, uuid
from celery import Celery

celery = Celery(__name__, broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"))

@celery.task
def ingest_from_url(url: str):
    # TODO: download with yt-dlp, transcribe (Whisper/WhisperX), index into search
    media_id = str(uuid.uuid4())
    return {"media_id": media_id, "url": url, "status": "stubbed"}