import json
import logging
from datetime import date
from typing import Any

import boto3
from dateutil.relativedelta import relativedelta

from .logging_config import configure_logging
from .main import run

logger = logging.getLogger(__name__)
configure_logging()

session = boto3.Session()


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Logic for lambda entrypoint."""
    prev_month: date = date.today() - relativedelta(months=1)  # day does not matter
    run(prev_month, session)
    return {"statusCode": 200, "body": json.dumps("Success!")}
