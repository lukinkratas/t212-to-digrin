import os
import time
from datetime import date, datetime
from io import BytesIO
from typing import Any
import pandas as pd
import json
import logging
import requests

import boto3
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from .t212 import Client as T212Client
from .logging_config import configure_logging
from .utils import log_func, decode_to_df, encode_df


logger = logging.getLogger(__name__)
configure_logging()

load_dotenv(override=True)

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']
t212 = T212Client(key=os.environ['T212_API_KEY'])


@log_func(logger.info)
def get_input_dt() -> date:
    prev_month: date = date.today() - relativedelta(months=1)  # day does not matter

    print('Reporting Year Month in "YYYY-mm" format:')
    print(f'Or confirm default "{prev_month.strftime("%Y-%m")}" by ENTER.')
    input_dt = input()

    if input_dt is None:
        return prev_month

    return datetime.strptime(input_dt, '%Y-%m')

@log_func(logger.info)
def create_report(from_dt: str | date | datetime, to_dt: str | date | datetime) -> dict[str, Any]:

    if isinstance(from_dt, (date, datetime)):
        from_dt = from_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    if isinstance(to_dt, (date, datetime)):
        to_dt = to_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    while True:
        report_id = t212.create_report(from_dt, to_dt)

        if report_id is None:
            logger.debug('No report export returned.)')
            time.sleep(15) # limit 1 call per 30s
            continue

    # optimized wait time for report creation
    time.sleep(1)

    while True:
        # reports: list of dicts with keys:
        #   reportId, timeFrom, timeTo, dataIncluded, status, downloadLink
        reports: list[dict[str, Any]] = t212.list_reports()

        if reports is None:
            logger.debug('No reports list returned.')
            time.sleep(30) # limit 1 call per 1min
            continue

        # filter report by report_id
        filtered_reports = [r for r in reports if r['reportId'] == report_id]

        if filtered_reports is []:
            logger.debug('Created report not found in reports list.')
            time.sleep(30) # limit 1 call per 1min
            continue

        # created report found
        report = filtered_reports[0]

        if report.get('status') == 'Finished':
            logger.debug('Report finished.')
            break

        logger.debug('Report not yet ready.')
        time.sleep(30)

    return report

@log_func(logger.info)
def transform_df(report_df: pd.DataFrame) -> pd.DataFrame:
    # Filter only buys and sells
    allowed_actions: list[str] = ['Market buy', 'Market sell']
    report_df = report_df[report_df['Action'].isin(allowed_actions)]
    logger.debug('Buys and filtered.')

    # Filter out blacklisted tickers
    ticker_blacklist: list[str] = [
        'VNTRF',  # due to stock split
        'BRK.A',  # not available in digrin
    ]
    report_df = report_df[~report_df['Ticker'].isin(ticker_blacklist)]

    # Apply the mapping to the ticker column
    ticker_map: dict[str, str] = {
        'VWCE': 'VWCE.DE',
        'VUAA': 'VUAA.DE',
        'SXRV': 'SXRV.DE',
        'ZPRV': 'ZPRV.DE',
        'ZPRX': 'ZPRX.DE',
        'MC': 'MC.PA',
        'ASML': 'ASML.AS',
        'CSPX': 'CSPX.L',
        'EISU': 'EISU.L',
        'IITU': 'IITU.L',
        'IUHC': 'IUHC.L',
        'NDIA': 'NDIA.L',
        'NUKL': 'NUKL.DE',
        'AVWS': 'AVWS.DE',
    }
    report_df['Ticker'] = report_df['Ticker'].replace(ticker_map)

    # convert dtypes
    return report_df.convert_dtypes()

@log_func(logger.info)
def download_report(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def main(input_dt: date) -> None:
    from_dt = input_dt.replace(day=1)
    to_dt = from_dt + relativedelta(months=1)

    report = create_report(from_dt, to_dt)

    t212_df_encoded = download_report(report['download_link'])

    filename: str = f'{input_dt.strftime("%Y-%m")}.csv'

    s3.upload_fileobj(
        Fileobj=BytesIO(t212_df_encoded), Bucket=BUCKET_NAME, Key=f't212/{filename}'
    )
    logger.debug('T212 CSV uploaded.')

    t212_df: pd.DataFrame = decode_to_df(t212_df_encoded)

    digrin_df: pd.DataFrame = transform_df(t212_df)

    digrin_df_encoded: bytes = encode_df(digrin_df)
    s3.upload_fileobj(
        Fileobj=BytesIO(digrin_df_encoded), Bucket=BUCKET_NAME, Key=f'digrin/{filename}'
    )

def lambda_handler(event, context):
    print(event)
    print(context)

    prev_month: date = date.today() - relativedelta(months=1)  # day does not matter
    main(prev_month)

    return {'statusCode': 200, 'body': json.dumps('Success!')}


if __name__ == '__main__':
    input_dt = get_input_dt()  # used later in the naming of csv
    main(input_dt)
