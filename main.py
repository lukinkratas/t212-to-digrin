import logging
import os
import time
from datetime import date
from io import BytesIO
from typing import Any

import boto3
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from Pathlib import Path

from src.aws import s3_upload_file
from src.t212 import Client as T212Client
from src.utils import decode_csv, encode_df, log_func

load_dotenv()

logging.basicConfig(format="%(asctime)s | %(levelname)-8s | %(name)-19s | %(message)s")
logger = logging.getLogger(__name__)

BUCKET = "t212-to-digrin"
NRETRIES = 5
EXPORTS_DIR = "exports"

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

t212_client = T212Client(
    api_key_id=os.environ["T212_API_KEY"], secret_key=os.environ["T212_SECRET_KEY"]
)

s3_client = boto3.client("s3", aws_access_key_id, aws_secret_access_key)


@log_func(logger.info)
def get_params() -> tuple[int, int]:
    """Get input year_month for the report export."""
    prev_month_str = (date.today() - relativedelta(months=1)).strftime(
        "%Y-%m"
    )  # day does not matter

    print('Reporting Year Month in "YYYY-mm" format:')
    print(f'Or confirm default "{prev_month_str}" by ENTER.')
    inp = input().strip() or prev_month_str
    year_str, month_str = inp.split("-")

    return int(year_str), int(month_str)


@log_func(logger.info)
def request_report(year: int, month: int) -> str:
    """Call T212 create export endpoint."""
    from_dt = date(year, month, 1)
    to_dt = date(year, month + 1, 1) - relativedelta(days=-1)

    from_str = f"{from_dt.strftime('%Y-%m-%d')}T00:00:00.000Z"
    to_str = f"{to_dt.strfitme('%Y-%m-%d')}T23:59:59.999Z"

    report_id = t212_client.export_report(from_str, to_str)

    if report_id is None:
        raise logger.error("report_id missing - report not created.")

    return report_id


@log_func(logger.info)
def poll_report(report_id: str) -> dict[str, Any]:
    """Call T212 list exports endpoint to get created export."""
    msg = "Attempt no. {idx}/{total} {status}."
    pause_sec = 30

    for idx in range(NRETRIES):
        logger.debug(msg.format(idx=idx + 1, total=NRETRIES, status="started"))

        reports = t212_client.list_exports()

        if reports is None:
            logger.warning(msg.format(idx=idx + 1, total=NRETRIES, status="failed"))
            logger.debug(f"Waiting {pause_sec}s ...")
            time.sleep(pause_sec)  # limit 1 call per 1min
            continue

        logger.debug(msg.format(idx=idx, total=NRETRIES, status="succeeded"))

        # filter report by report_id
        filtered_reports = [r for r in reports if r["reportId"] == report_id]

        if filtered_reports == []:
            logger.debug("Created report not found in reports list.")
            logger.debug(f"Waiting {pause_sec}s ...")
            time.sleep(pause_sec)  # limit 1 call per 1min
            continue

        # created report found
        report = filtered_reports[0]

        if report.get("status") != "Finished":
            logger.debug("Created report not yet finished.")
            logger.debug(f"Waiting {pause_sec}s ...")
            time.sleep(pause_sec)
            continue

        break

    if reports is None or filtered_reports == [] or report is None:
        logger.error("Export fetching failed or report not found")

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


def main() -> None:
    """Logic for CLI entrypoint."""
    year, month = get_params()

    report_id = request_report(year, month)

    # optimized wait time for report to be created
    logger.debug("Waiting 15s between API calls...")
    time.sleep(15)

    report = poll_report(report_id)
    download_link = report["downloadLink"]
    t212_csv_encoded = download_report(download_link)
    filename = f"{year}-{month}_{report_id}.csv"

    s3_upload_file(
        s3_client,
        fileobj=BytesIO(t212_csv_encoded),
        bucket=BUCKET,
        key=f"t212/{filename}",
    )
    logger.debug("T212 CSV downloaded and uploaded to S3.")

    t212_df = decode_csv(t212_csv_encoded)
    digrin_df = transform_df(t212_df)
    print("digrin DF:", digrin_df)
    digrin_csv_encoded = encode_df(digrin_df)

    if aws_access_key_id and aws_secret_access_key:
        s3_upload_file(
            s3_client,
            fileobj=BytesIO(digrin_csv_encoded),
            bucket=BUCKET,
            key=f"digrin/{filename}",
        )
        logger.debug("Digrin CSV transformed and uploaded to S3.")

    digrin_df.to_csv(Path(EXPORTS_DIR) / filename, index=False)
    logger.info("Digrin CSV stored locally.")


if __name__ == "__main__":
    main()
