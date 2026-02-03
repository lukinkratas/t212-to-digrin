import json
import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from .logging_config import configure_logging
from .main import run

logger = logging.getLogger(__name__)
configure_logging()


def lambda_handler(event, context):
    """Logic for lambda entrypoint."""
    print(event)
    print(context)

    prev_month: date = date.today() - relativedelta(months=1)  # day does not matter
    run(prev_month)

    return {"statusCode": 200, "body": json.dumps("Success!")}
