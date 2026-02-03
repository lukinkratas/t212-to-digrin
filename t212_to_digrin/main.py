import os
import time
from datetime import date, datetime
from io import BytesIO
from typing import Any
import pandas as pd
import logging
import requests
from requests.exceptions import HTTPError

import boto3
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from .t212 import Client as T212Client
from .utils import log_func, decode_to_df, encode_df


logger = logging.getLogger(__name__)

load_dotenv(override=True)

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']
t212 = T212Client(key=os.environ['T212_API_KEY'])
NRETRIES = 3

@log_func(logger.info)
def create_report(from_dt: str | date | datetime, to_dt: str | date | datetime) -> dict[str, Any]:

    if isinstance(from_dt, (date, datetime)):
        from_dt = from_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    if isinstance(to_dt, (date, datetime)):
        to_dt = to_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    msg = 'POST export attempt no. {idx}/{total} {status}.'

    for idx in range(1, NRETRIES+1):

        logger.debug(msg.format(idx=idx, total=NRETRIES, status='started'))

        try:
            report_id = t212.create_report(from_dt, to_dt)

        except HTTPError:
            logger.warning(msg.format(idx=idx, total=NRETRIES, status='failed') + 'Waiting 15s...')
            time.sleep(15) # limit 1 call per 30s
            continue

        logger.debug(msg.format(idx=idx, total=NRETRIES, status='succeeded'))
        break

    # optimized wait time for report creation
    logger.debug(f'Waiting 10s between API calls...')
    time.sleep(10)

    msg = 'GET history exports attempt no. {idx}/{total} {status}.'

    for idx in range(1, NRETRIES+1):

        logger.debug(msg.format(idx=idx, total=NRETRIES, status='started'))

        try:
            reports = t212.list_reports()

        except HTTPError:
            logger.warning(msg.format(idx=idx, total=NRETRIES, status='failed') + 'Waiting 30s ...')
            time.sleep(30) # limit 1 call per 1min
            continue

        logger.debug(msg.format(idx=idx, total=NRETRIES, status='succeeded'))

        # filter report by report_id
        filtered_reports = [r for r in reports if r['reportId'] == report_id]

        if filtered_reports is []:
            logger.debug('Created report not found in reports list.')
            time.sleep(30) # limit 1 call per 1min
            continue

        # created report found
        report = filtered_reports[0]

        if report.get('status') != 'Finished':
            logger.debug('Created report not yet finished.')
            time.sleep(30)
            continue

        break

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

@log_func(logger.info)
def run(input_dt: date) -> None:
    from_dt = input_dt.replace(day=1)
    to_dt = from_dt + relativedelta(months=1)

    report = create_report(from_dt, to_dt)
    download_link = report["downloadLink"]

    t212_df_encoded = download_report(report['downloadLink'])

    filename: str = f'{input_dt.strftime("%Y-%m")}.csv'

    s3.upload_fileobj(
        Fileobj=BytesIO(t212_df_encoded), Bucket=BUCKET_NAME, Key=f't212/{filename}'
    )
    logger.debug('T212 CSV downloaded and uploaded to S3.')

    t212_df: pd.DataFrame = decode_to_df(t212_df_encoded)

    digrin_df: pd.DataFrame = transform_df(t212_df)

    digrin_df_encoded: bytes = encode_df(digrin_df)
    s3.upload_fileobj(
        Fileobj=BytesIO(digrin_df_encoded), Bucket=BUCKET_NAME, Key=f'digrin/{filename}'
    )
    logger.debug('Digrin CSV transformed and uploaded to S3.')

    digrin_csv_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': f'digrin/{filename}'},
        ExpiresIn=120, # 2min
    )
    logger.info(f'Digrin CSV url: {digrin_csv_url}')
