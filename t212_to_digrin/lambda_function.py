import json
import logging
from datetime import date
from functools import lru_cache
from typing import Any

from boto3 import Session
from botocore.client import BaseClient
from dateutil.relativedelta import relativedelta

from .aws import send_email
from .logging_config import configure_logging
from .main import run

logger = logging.getLogger(__name__)
configure_logging()

session = Session()


@lru_cache
def _get_ses_client(session: Session) -> BaseClient:
    """Lazy init ses client."""
    return session.client("ses")


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Logic for lambda entrypoint."""
    prev_month = date.today() - relativedelta(months=1)  # day does not matter
    digrin_csv_url = run(prev_month, session, generate_presigned_url=True)
    ses_client = _get_ses_client(session)
    message = {
        "Subject": {
            "Data": "[t212-to-digrin] New Digrin CSV Available",
            "Charset": "UTF-8",
        },
        "Body": {
            "Html": {
                "Data": (
                    "<html>"
                    "<body>"
                    "<p>Wazzuuup</p>"
                    "<p>"
                    f"  {prev_month.strftime('%b %Y')} CSV can be downloaded "
                    f"<a href='{digrin_csv_url}'>here</a>"
                    "."
                    "</p>"
                    "</body>"
                    "</html>"
                ),
                "Charset": "UTF-8",
            }
        },
    }
    send_email(ses_client, message)
    return {"statusCode": 200, "body": json.dumps("Success!")}
