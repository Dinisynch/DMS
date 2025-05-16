from datetime import timedelta
from app.core.config import settings
from app.models import Document

from app.core.minio_client import minio_client

def build_file_url(document: Document) -> str | None:
    if not document.file_path:
        return None
    return minio_client.presigned_get_object(
        bucket_name=settings.minio_bucket_name,
        object_name=document.file_path,
        expires=timedelta(minutes=10)
    )