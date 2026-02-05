import pytest
from datetime import date
import pathlib

from pandas.testing import assert_frame_equal
import pandas as pd
from dateutil.relativedelta import relativedelta

from t212_to_digrin.main import create_report, upload_to_aws, transform_df
from t212_to_digrin.utils import encode_df


def get_csv_fixture(filename: str) -> pd.DataFrame:
    fixture_path = pathlib.Path(__file__).resolve().parent.joinpath('fixtures')
    return pd.read_csv(fixture_path.joinpath(filename))


@pytest.fixture
def t212_df() -> pd.DataFrame:
    return get_csv_fixture('t212.csv')

@pytest.fixture
def digrin_df() -> pd.DataFrame:
    return get_csv_fixture('digrin.csv')

def test_create_report() -> None:
    # mock t212 calls

    from_dt = date.today()
    to_dt = from_dt + relativedelta(months=1)
    # create_report(from_dt, to_dt)


def test_transform_df(t212_df: pd.DataFrame, digrin_df: pd.DataFrame) -> None:
    assert_frame_equal(transform_df(t212_df), digrin_df, check_dtype=False)


def test_upload_to_aws(t212_df: pd.DataFrame) -> None:
    # mock aws calls

    t212_df_encoded = encode_df(t212_df)
    filename = "YYYY-mm.csv"
    generate_download_url = True
    # upload_to_aws(t212_df_encoded, filename, generate_download_url)
    pass
