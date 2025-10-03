from __future__ import annotations

from datetime import timedelta
from io import BytesIO

from minio import Minio

from app.core.config import get_settings

settings = get_settings()
_secure = settings.s3_endpoint.startswith("https://")
_client = Minio(
    settings.s3_endpoint.replace("http://", "").replace("https://", ""),
    access_key=settings.s3_access_key,
    secret_key=settings.s3_secret_key,
    secure=_secure,
)


def ensure_bucket(bucket: str | None = None) -> None:
    bucket_name = bucket or settings.s3_bucket
    if not _client.bucket_exists(bucket_name):
        _client.make_bucket(bucket_name)


def upload_bytes(key: str, data: bytes, content_type: str, bucket: str | None = None) -> None:
    bucket_name = bucket or settings.s3_bucket
    ensure_bucket(bucket_name)
    _client.put_object(bucket_name, key, BytesIO(data), len(data), content_type=content_type)


def download_bytes(key: str, bucket: str | None = None) -> bytes:
    bucket_name = bucket or settings.s3_bucket
    response = _client.get_object(bucket_name, key)
    data = response.read()
    response.close()
    response.release_conn()
    return data


def get_presigned_url(key: str, bucket: str | None = None, expires: timedelta = timedelta(hours=1)) -> str:
    bucket_name = bucket or settings.s3_bucket
    return _client.presigned_get_object(bucket_name, key, expires=expires)
