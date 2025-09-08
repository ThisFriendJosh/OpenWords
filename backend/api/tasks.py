"""Background tasks for media ingestion and transcription."""

import json
import os
import tempfile
import uuid
from typing import List, Dict

import boto3
from botocore.exceptions import ClientError
from celery import Celery
from celery.utils.log import get_task_logger

from .search import index_transcript


logger = get_task_logger(__name__)


# Configure Celery using Redis as the broker by default
celery = Celery(__name__, broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"))


@celery.task(bind=True)
def ingest_from_url(self, url: str) -> Dict[str, str]:
    """Download media from a URL, transcribe it and index the transcript.

    The task reports progress via custom states:
    ``DOWNLOADING`` -> ``TRANSCRIBING`` -> ``UPLOADING`` -> ``INDEXING``.

    Args:
        url: Remote media URL supported by yt-dlp.

    Returns:
        A dictionary containing the media ID, original URL and final status.

    Raises:
        Exception: Any exception is propagated after updating the task state to
        ``FAILURE``. This allows Celery to record the failure while ensuring the
        error is visible to clients polling for status.
    """

    media_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp()
    file_path = None

    try:
        # ------------------------------ Download -----------------------------
        self.update_state(state="DOWNLOADING")

        import yt_dlp

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
            "quiet": True,
            "noprogress": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # ---------------------------- Transcription -------------------------
        self.update_state(state="TRANSCRIBING")

        import whisperx

        model_name = os.getenv("WHISPER_MODEL", "base")
        device = os.getenv("WHISPER_DEVICE", "cpu")
        compute_type = "int8" if device == "cpu" else "float16"

        model = whisperx.load_model(model_name, device, compute_type=compute_type)
        result = model.transcribe(file_path)
        segments: List[Dict] = result.get("segments", [])

        # ------------------------------ Storage -----------------------------
        self.update_state(state="UPLOADING")

        s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("MINIO_URL", "http://minio:9000"),
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minio"),
            aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minio123"),
            region_name=os.getenv("MINIO_REGION", "us-east-1"),
        )
        bucket = os.getenv("TRANSCRIPTS_BUCKET", "transcripts")

        try:
            s3.head_bucket(Bucket=bucket)
        except ClientError:
            s3.create_bucket(Bucket=bucket)

        s3.put_object(
            Bucket=bucket,
            Key=f"{media_id}.json",
            Body=json.dumps(segments).encode("utf-8"),
            ContentType="application/json",
        )

        # ------------------------------- Index ------------------------------
        self.update_state(state="INDEXING")
        index_transcript(media_id, segments)

        return {"media_id": media_id, "url": url, "status": "completed"}

    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Ingestion failed: %s", exc)
        self.update_state(state="FAILURE", meta={"exc": str(exc)})
        raise

    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass

import os, uuid
from celery import Celery

celery = Celery(__name__, broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"))

@celery.task
def ingest_from_url(url: str):
    # TODO: download with yt-dlp, transcribe (Whisper/WhisperX), index into search
    media_id = str(uuid.uuid4())
    return {"media_id": media_id, "url": url, "status": "stubbed"}
