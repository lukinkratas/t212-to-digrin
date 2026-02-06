import json
import logging
from functools import lru_cache
from typing import Any, Callable

import boto3
from botocore.exceptions import ClientError
from botocore.client import BaseClient

from .utils import log_func

logger = logging.getLogger(__name__)


@lru_cache
def _get_session() -> boto3.Session:
    """Lazy init session."""
    return boto3.Session(profile_name="t212-to-digrin-cli")


@lru_cache
def _get_secrets_client() -> BaseClient:
    """Lazy init secrets client."""
    return _get_session().client("secretsmanager")


@lru_cache
def _get_s3_client() -> BaseClient:
    """Lazy init s3 client."""
    return _get_session().client("s3")


def _request(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Wrap boto function in try-except block."""
    try:
        response = func(*args, **kwargs)

    except ClientError as e:
        logging.error(e)
        raise e

    return response


@log_func(logger.debug)
def get_secret(secret_name: str) -> str:
    """Fetch secret key-value pairs from Secrets Manager Service."""
    secrets_client = _get_secrets_client()
    response = _request(secrets_client.get_secret_value, SecretId=secret_name)
    return json.loads(response["SecretString"])


@log_func(logger.debug)
def upload_file(fileobj: bytes, bucket: str, key: str) -> None:
    """Upload file bytes to S3 service."""
    s3_client = _get_s3_client()
    _request(s3_client.upload_fileobj, Fileobj=fileobj, Bucket=bucket, Key=key)


@log_func(logger.debug)
def get_download_url(bucket: str, key: str) -> str:
    """Generate a download url for file stored in S3 service."""
    s3_client = _get_s3_client()
    return _request(
        s3_client.generate_presigned_url,
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=60,  # 1min
    )
