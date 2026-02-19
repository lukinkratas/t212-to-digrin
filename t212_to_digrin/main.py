import logging
import sys
import time
from datetime import date, datetime
from functools import lru_cache
from io import BytesIO
from typing import Any

import pandas as pd
import requests
from boto3 import Session
from botocore.client import BaseClient
from dateutil.relativedelta import relativedelta

from .aws import get_presigned_url, get_secret, upload_file
from .t212 import Client as T212Client
from .utils import decode_csv, encode_df, log_func

logger = logging.getLogger(__name__)

BUCKET = "t212-to-digrin"
NRETRIES = 5


@lru_cache
def _get_secrets_client(session: Session) -> BaseClient:
    """Lazy init secrets client."""
    return session.client("secretsmanager")


@lru_cache
def _get_s3_client(session: Session) -> BaseClient:
    """Lazy init s3 client."""
    return session.client("s3")


@lru_cache
def _get_t212_client(secrets_client: BaseClient) -> T212Client:
    """Lazy init t212.Client."""
    secret = get_secret(secrets_client, "t212-to-digrin")
    return T212Client(
        api_key_id=secret["T212_API_KEY_ID"],
        secret_key=secret["T212_SECRET_KEY"],
    )


@log_func(logger.info)
def create_report(
    session: Session,
    from_dt: str | date | datetime,
    to_dt: str | date | datetime,
) -> dict[str, Any]:
    """Call T212 endpoints for report exporting and listing reports."""
    if isinstance(from_dt, (date, datetime)):
        from_dt = from_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    if isinstance(to_dt, (date, datetime)):
        to_dt = to_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    secrets_client = _get_secrets_client(session)
    t212_client = _get_t212_client(secrets_client)
    msg = "Attempt no. {idx}/{total} {status}."

    for idx in range(1, NRETRIES + 1):
        logger.debug(msg.format(idx=idx, total=NRETRIES, status="started"))
        report_id = t212_client.export_report(from_dt, to_dt)

        if report_id is None:
            logger.warning(msg.format(idx=idx, total=NRETRIES, status="failed"))
            logger.debug("Waiting 15s...")
            time.sleep(15)  # limit 1 call per 30s
            continue

        logger.debug(msg.format(idx=idx, total=NRETRIES, status="succeeded"))
        break

    if report_id is None:
        sys.exit(1)

    # optimized wait time for report to be created
    logger.debug("Waiting 10s between API calls...")
    time.sleep(10)

    for idx in range(1, NRETRIES + 1):
        logger.debug(msg.format(idx=idx, total=NRETRIES, status="started"))

        reports = t212_client.list_exports()

        if reports is None:
            logger.warning(msg.format(idx=idx, total=NRETRIES, status="failed"))
            logger.debug("Waiting 30s ...")
            time.sleep(30)  # limit 1 call per 1min
            continue

        logger.debug(msg.format(idx=idx, total=NRETRIES, status="succeeded"))

        # filter report by report_id
        filtered_reports = [r for r in reports if r["reportId"] == report_id]

        if filtered_reports == []:
            logger.debug("Created report not found in reports list.")
            logger.debug("Waiting 30s ...")
            time.sleep(30)  # limit 1 call per 1min
            continue

        # created report found
        report = filtered_reports[0]

        if report.get("status") != "Finished":
            logger.debug("Created report not yet finished.")
            logger.debug("Waiting 30s ...")
            time.sleep(30)
            continue

        break

    if reports is None or filtered_reports == [] or report is None:
        sys.exit(1)

    return report


@log_func(logger.info)
def transform_df(report_df: pd.DataFrame) -> pd.DataFrame:
    """Transform Pandas Dataframe - perform filtering and remapping."""
    # Filter only buys and sells
    allowed_actions: list[str] = ["Market buy", "Market sell"]
    report_df = report_df[report_df["Action"].isin(allowed_actions)]

    # Filter out blacklisted tickers
    ticker_blacklist: list[str] = [
        "VNTRF",  # due to stock split
        "BRK.A",  # not available in digrin
    ]
    report_df = report_df[~report_df["Ticker"].isin(ticker_blacklist)]

    # Apply the mapping to the ticker column
    ticker_map: dict[str, str] = {
        "MC": "MC.PA",
        "ASML": "ASML.AS",
        "VWCE": "VWCE.DE",
        "VUAA": "VUAA.DE",
        "SXRV": "SXRV.DE",
        "ZPRV": "ZPRV.DE",
        "ZPRX": "ZPRX.DE",
        "NUKL": "NUKL.DE",
        "AVWS": "AVWS.DE",
        "CSPX": "CSPX.L",
        "EISU": "EISU.L",
        "IITU": "IITU.L",
        "IUHC": "IUHC.L",
        "NDIA": "NDIA.L",
    }
    report_df["Ticker"] = report_df["Ticker"].replace(ticker_map)

    return report_df.convert_dtypes().reset_index(drop=True)


@log_func(logger.info)
def download_report(url: str) -> bytes:
    """Download bytes from url content."""
    response = requests.get(url)
    response.raise_for_status()
    return response.content


@log_func(logger.info)
def upload_to_aws(
    session: Session,
    t212_csv_encoded: bytes,
    filename: str,
    store_locally: bool = False,
    generate_presigned_url: bool = False,
) -> str | None:
    """Call AWS endpoints to store csvs."""
    s3_client = _get_s3_client(session)

    upload_file(
        s3_client,
        fileobj=BytesIO(t212_csv_encoded),
        bucket=BUCKET,
        key=f"t212/{filename}",
    )
    logger.debug("T212 CSV downloaded and uploaded to S3.")

    t212_df = decode_csv(t212_csv_encoded)
    digrin_df = transform_df(t212_df)
    digrin_csv_encoded = encode_df(digrin_df)
    upload_file(
        s3_client,
        fileobj=BytesIO(digrin_csv_encoded),
        bucket=BUCKET,
        key=f"digrin/{filename}",
    )
    logger.debug("Digrin CSV transformed and uploaded to S3.")

    if store_locally:
        digrin_df.to_csv(filename, index=False)
        logger.info("Digrin CSV stored locally.")

    if generate_presigned_url:
        digrin_csv_url = get_presigned_url(
            s3_client, bucket=BUCKET, key=f"digrin/{filename}"
        )
        logger.info(f"Digrin CSV url: {digrin_csv_url}")
        return digrin_csv_url


@log_func(logger.info)
def run(
    input_dt: date,
    session: Session,
    store_locally: bool = False,
    generate_presigned_url: bool = False,
) -> str | None:
    """Common runner logic shared between CLI and lambda entrypoints."""
    from_dt = input_dt.replace(day=1)
    to_dt = from_dt + relativedelta(months=1)

    report = create_report(session, from_dt, to_dt)
    download_link = report["downloadLink"]

    return upload_to_aws(
        session,
        t212_csv_encoded=download_report(download_link),
        filename=f"{input_dt.strftime('%Y-%m')}.csv",
        store_locally=store_locally,
        generate_presigned_url=generate_presigned_url,
    )
