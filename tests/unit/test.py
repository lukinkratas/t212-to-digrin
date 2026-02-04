from datetime import date

import pandas as pd
from dateutil.relativedelta import relativedelta

from t212_to_digrin.main import create_report, run, transform_df


def test_create_report() -> None:
    # mock t212 calls
    from_dt = date.today()
    to_dt = from_dt + relativedelta(months=1)
    create_report(from_dt, to_dt)


def test_transform_df() -> None:
    data = {
        "Action": [],
        "Time": [],
        "ISIN": [],
        "Ticker": [],
        "Name": [],
        "Notes": [],
        "ID": [],
        "No. of shares": [],
        "Price / share": [],
        "Currency (Price / share)": [],
        "Exchange rate": [],
        "Result": [],
        "Currency (Result)": [],
        "Total": [],
        "Currency (Total)": [],
        "Withholding tax": [],
        "Currency (Withholding tax)": [],
        "Currency conversion from amount": [],
        "Currency (Currency conversion from amount)": [],
        "Currency conversion to amount": [],
        "Currency (Currency conversion to amount)": [],
        "Currency conversion fee": [],
        "Currency (Currency conversion fee": [],
    }

    allowed_actions: list[str] = ["Market buy", "Market sell"]
    ticker_blacklist: list[str] = [
        "VNTRF",  # due to stock split
        "BRK.A",  # not available in digrin
    ]
    ticker_map: dict[str, str] = {
        "VWCE": "VWCE.DE",
        "VUAA": "VUAA.DE",
        "SXRV": "SXRV.DE",
        "ZPRV": "ZPRV.DE",
        "ZPRX": "ZPRX.DE",
        "MC": "MC.PA",
        "ASML": "ASML.AS",
        "CSPX": "CSPX.L",
        "EISU": "EISU.L",
        "IITU": "IITU.L",
        "IUHC": "IUHC.L",
        "NDIA": "NDIA.L",
        "NUKL": "NUKL.DE",
        "AVWS": "AVWS.DE",
    }
    report_df = pd.DataFrame()
    transform_df(report_df)


def test_run() -> None:
    # mock t212 calls
    # mock aws calls
    input_dt = date.today()
    generate_download_url = True
    run(input_dt, generate_download_url)
