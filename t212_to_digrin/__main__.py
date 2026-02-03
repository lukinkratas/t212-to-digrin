from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging

from .main import run
from .utils import log_func
from .logging_config import configure_logging

logger = logging.getLogger(__name__)
configure_logging()

@log_func(logger.info) # unable to log with input
def get_input_dt() -> date:
    prev_month: date = date.today() - relativedelta(months=1)  # day does not matter

    print('Reporting Year Month in "YYYY-mm" format:')
    print(f'Or confirm default "{prev_month.strftime("%Y-%m")}" by ENTER.')
    inp = input()

    if inp == '':
        return prev_month

    return datetime.strptime(inp, '%Y-%m')

def main() -> None:
    input_dt = get_input_dt()
    run(input_dt)

if __name__ == "__main__":
    main()
