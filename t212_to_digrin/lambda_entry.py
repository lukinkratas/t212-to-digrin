from datetime import date
from dateutil.relativedelta import relativedelta
import json
import logging

from .main import run
from .logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()

def lambda_handler(event, context):
    print(event)
    print(context)

    prev_month: date = date.today() - relativedelta(months=1)  # day does not matter
    run(prev_month)

    return {'statusCode': 200, 'body': json.dumps('Success!')}
