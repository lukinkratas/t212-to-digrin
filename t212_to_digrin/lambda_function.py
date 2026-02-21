import json
import logging
from datetime import date, datetime
from functools import lru_cache
from typing import Any

from boto3 import Session
from botocore.client import BaseClient
from dateutil.relativedelta import relativedelta

from .aws import ses_send_email
from .logging_config import configure_logging
from .main import run

logger = logging.getLogger(__name__)
configure_logging()

session = Session()


@lru_cache
def _get_ses_client(session: Session) -> BaseClient:
    """Lazy init ses client."""
    return session.client("ses")


def send_email(session: Session, dt: date | datetime, url: str):
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
                    "<p></p>"
                    "<p>"
                    f"{dt.strftime('%b %Y')} CSV can be downloaded "
                    f"<a href='{url}'>here</a>"
                    "."
                    "</p>"
                    "</body>"
                    "</html>"
                ),
                "Charset": "UTF-8",
            }
        },
    }
    ses_send_email(ses_client, message)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Logic for lambda entrypoint."""
    prev_month = date.today() - relativedelta(months=1)  # day does not matter
    digrin_csv_url = run(prev_month, session, generate_presigned_url=True)
    send_email(session, prev_month, digrin_csv_url)
    return {"statusCode": 200, "body": json.dumps("Success!")}
