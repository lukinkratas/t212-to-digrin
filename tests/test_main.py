import json
import pathlib
from datetime import date
from typing import Any

import pandas as pd
import pytest
from dateutil.relativedelta import relativedelta
from pandas.testing import assert_frame_equal
from pytest_mock import MockerFixture

from t212_to_digrin.main import create_report, transform_df, upload_to_aws
from t212_to_digrin.utils import encode_df

FIXTURE_PATH = pathlib.Path(__file__).resolve().parent.joinpath("fixtures")


def get_csv_fixture(filename: str) -> pd.DataFrame:
    return pd.read_csv(FIXTURE_PATH.joinpath(filename))


def get_json_fixture(filename: str) -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.joinpath(filename).read_text())


@pytest.fixture
def t212_df() -> pd.DataFrame:
    return get_csv_fixture("t212.csv")


@pytest.fixture
def digrin_df() -> pd.DataFrame:
    return get_csv_fixture("digrin.csv")


@pytest.fixture
def export() -> dict[str, Any]:
    return get_json_fixture("export.json")


@pytest.fixture
def secret() -> dict[str, str]:
    return {"API_KEY_ID": "xxx", "SECRET_KEY": "xxx"}


@pytest.fixture(autouse=True)
def mock_sleep(mocker: MockerFixture) -> None:
    """Skip all sleep calls in tests."""
    mocker.patch("time.sleep", return_value=None)


def test_transform_df(t212_df: pd.DataFrame, digrin_df: pd.DataFrame) -> None:
    assert_frame_equal(transform_df(t212_df), digrin_df, check_dtype=False)


def test_create_report(
    mocker: MockerFixture,
    secret: dict[str, str],
    export: dict[str, int],
    mock_sleep: None,
) -> None:
    mocker.patch("t212_to_digrin.main.get_secret", return_value=secret)

    mock_client = mocker.Mock()
    mock_client.export_report.return_value = export["reportId"]
    mock_client.list_exports.return_value = [export]
    mocker.patch("t212_to_digrin.main._get_t212_client", return_value=mock_client)

    session = mocker.Mock()
    from_dt = date.today()
    to_dt = from_dt + relativedelta(months=1)
    assert create_report(session, from_dt, to_dt) == export


def test_upload_to_aws(t212_df: pd.DataFrame, mocker: MockerFixture) -> None:
    mocker.patch("t212_to_digrin.main.upload_file", return_value=None)
    mocker.patch(
        "t212_to_digrin.main.get_download_url",
        return_value="https://t212-to-digrin.s3.amazonaws.com/xxx/YYYY-mm.csv?X-Amz-Algorithm=xxx&X-Amz-Credential=xxx&X-Amz-Date=xxx&X-Amz-Expires=xxx&X-Amz-SignedHeaders=host&X-Amz-Signature=xxx",
    )

    upload_to_aws(
        session=mocker.Mock(),
        t212_csv_encoded=encode_df(t212_df),
        filename="YYYY-mm.csv",
        store_locally=False,
        generate_presigned_url=True,
    )
