import logging
from datetime import date, datetime

import boto3
from dateutil.relativedelta import relativedelta

from .logging_config import configure_logging
from .main import run
from .utils import log_func

logger = logging.getLogger(__name__)
configure_logging()

session = boto3.Session(profile_name="t212-to-digrin-cli")


@log_func(logger.info)  # unable to log with input
def get_input_dt() -> date:
    """Get input year_month for the report export."""
    prev_month: date = date.today() - relativedelta(months=1)  # day does not matter

    print('Reporting Year Month in "YYYY-mm" format:')
    print(f'Or confirm default "{prev_month.strftime("%Y-%m")}" by ENTER.')
    inp = input()

    if inp == "":
        return prev_month

    return datetime.strptime(inp, "%Y-%m")


def main() -> None:
    """Logic for CLI entrypoint."""
    input_dt = get_input_dt()
    run(input_dt, session, generate_download_url=True)


if __name__ == "__main__":
    main()
