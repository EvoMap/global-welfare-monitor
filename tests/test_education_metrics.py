"""Tests for unesco_education.py -- verifies UNESCO UIS data fetching and validation."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.unesco_education import UNESCOEducationData


@pytest.fixture
def edu():
    return UNESCOEducationData(api_url="http://mock-api/")


def test_fetch_data_success(edu):
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{"country": "USA", "year": 2020, "value": 99}]
    mock_resp.raise_for_status = MagicMock()

    with patch("src.unesco_education.requests.get", return_value=mock_resp):
        result = edu.fetch_data("data", params={"indicator": "TEST"})
    assert result is not None
    assert len(result) == 1


def test_fetch_data_network_error(edu):
    from requests.exceptions import ConnectionError as ReqConnectionError
    with patch("src.unesco_education.requests.get", side_effect=ReqConnectionError("timeout")):
        result = edu.fetch_data("data")
    assert result is None


def test_get_education_data_success(edu):
    api_response = [
        {"country": "USA", "year": 2020, "value": 95.0},
        {"country": "CAN", "year": 2020, "value": 98.0},
    ]
    with patch.object(edu, "fetch_data", return_value=api_response):
        df = edu.get_education_data()
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert "Country" in df.columns
    assert "Value" in df.columns
    assert len(df) > 0


def test_get_education_data_no_data(edu):
    with patch.object(edu, "fetch_data", return_value=None):
        df = edu.get_education_data()
    assert df is None


def test_validate_data_valid(edu):
    df = pd.DataFrame({"Country": ["USA"], "Year": [2020], "Indicator": ["Test"], "Value": [95.0]})
    assert edu.validate_data(df) is True


def test_validate_data_missing_values(edu):
    df = pd.DataFrame({"Country": [None], "Year": [2020], "Indicator": ["Test"], "Value": [95.0]})
    assert edu.validate_data(df) is False


def test_validate_data_non_numeric_value(edu):
    df = pd.DataFrame({"Country": ["USA"], "Year": [2020], "Indicator": ["Test"], "Value": ["abc"]})
    assert edu.validate_data(df) is False


def test_save_data(edu, tmp_path):
    df = pd.DataFrame({"Country": ["USA"], "Year": [2020], "Indicator": ["Test"], "Value": [95.0]})
    filepath = str(tmp_path / "test_edu.csv")
    edu.save_data(df, filepath)
    loaded = pd.read_csv(filepath)
    assert len(loaded) == 1
