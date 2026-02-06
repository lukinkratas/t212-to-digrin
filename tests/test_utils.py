import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from t212_to_digrin.utils import decode_csv, encode_df


@pytest.fixture
def encoded_csv() -> bytes:
    return (
        b"Action,Time,Price,Currency\n"
        b"Market sell,2026-01-01 01:01:01,1.0,EUR\n"
        b"Market buy,2026-01-01 01:01:01,1.0,USD\n"
    )


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Action": ["Market sell", "Market buy"],
            "Time": ["2026-01-01 01:01:01", "2026-01-01 01:01:01"],
            "Price": [1.0, 1.0],
            "Currency": ["EUR", "USD"],
        }
    )


def test_decode_csv(encoded_csv: bytes, df: pd.DataFrame) -> None:
    assert_frame_equal(decode_csv(encoded_csv), df)


def test_encode_df(encoded_csv: bytes, df: pd.DataFrame) -> None:
    assert encode_df(df) == encoded_csv
