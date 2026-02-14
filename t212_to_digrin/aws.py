import json
import logging
from typing import Any, Callable

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from .utils import log_func

logger = logging.getLogger(__name__)


def _request(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Wrap boto function in try-except block."""
    try:
        response = func(*args, **kwargs)

    except ClientError as e:
        logging.error(e)
        raise e

    return response


@log_func(logger.debug)
def get_secret(secrets_client: BaseClient, secret_name: str) -> str:
    """Fetch secret key-value pairs from Secrets Manager Service."""
    response = _request(secrets_client.get_secret_value, SecretId=secret_name)
    return json.loads(response["SecretString"])


@log_func(logger.debug)
def upload_file(s3_client: BaseClient, fileobj: bytes, bucket: str, key: str) -> None:
    """Upload file bytes to S3 service."""
    _request(s3_client.upload_fileobj, Fileobj=fileobj, Bucket=bucket, Key=key)


@log_func(logger.debug)
def get_download_url(s3_client: BaseClient, bucket: str, key: str) -> str:
    """Generate a download url for file stored in S3 service."""
    return _request(
        s3_client.generate_presigned_url,
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=60,  # 1min
    )
