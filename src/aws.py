import logging

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from .utils import log_func

logger = logging.getLogger(__name__)


@log_func(logger.debug)
def s3_upload_file(
    s3_client: BaseClient, fileobj: bytes, bucket: str, key: str
) -> None:
    """Upload file bytes to S3 service."""
    try:
        s3_client.upload_fileobj(Fileobj=fileobj, Bucket=bucket, Key=key)

    except ClientError as e:
        logging.error(e)
        raise e
