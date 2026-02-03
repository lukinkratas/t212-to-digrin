import json
import logging
import boto3
from botocore.exceptions import ClientError

from .utils import log_func

logger = logging.getLogger(__name__)

secrets_manager = boto3.client('secretsmanager')
s3 = boto3.client('s3')

@log_func(logger.debug)
def get_secret(secret_name: str) -> str:

    try:
        response = secrets_manager.get_secret_value(SecretId=secret_name)

    except ClientError as e:
        logging.error(e)
        raise e

    return json.loads(response['SecretString'])

@log_func(logger.debug)
def upload_file(fileobj: bytes, bucket: str, key:str) -> None:

    try:
        response = s3.upload_fileobj(
            Fileobj=fileobj,
            Bucket=bucket,
            Key=key,
        )

    except ClientError as e:
        logging.error(e)
        raise e

@log_func(logger.debug)
def get_download_url(bucket: str, key: str) -> str:

    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=120, # 2min
        )
    except ClientError as e:
        logging.error(e)
        raise e

    return url

