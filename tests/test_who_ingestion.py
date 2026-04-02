"""Tests for who_api_ingestion.py -- verifies WHO GHO API data fetching."""

import pytest
from unittest.mock import patch, MagicMock
from src.who_api_ingestion import fetch_data, main


class _MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"HTTP {self.status_code}")


def test_fetch_data_success():
    payload = {"value": [{"SpatialDim": "USA", "NumericValue": 78.0}]}
    with patch("src.who_api_ingestion.requests.get") as mock_get:
        mock_get.return_value = _MockResponse(payload)
        result = fetch_data("WHOSIS_000001")
    assert result is not None
    assert len(result) == 1
    assert result[0]["SpatialDim"] == "USA"


def test_fetch_data_failure():
    from requests.exceptions import ConnectionError as ReqConnectionError
    with patch("src.who_api_ingestion.requests.get") as mock_get:
        mock_get.side_effect = ReqConnectionError("connection error")
        result = fetch_data("WHOSIS_000001")
    assert result is None


def test_fetch_data_empty_value():
    payload = {"value": []}
    with patch("src.who_api_ingestion.requests.get") as mock_get:
        mock_get.return_value = _MockResponse(payload)
        result = fetch_data("WHOSIS_000001")
    assert result == []


def test_main_creates_csv(tmp_path):
    sample_record = {
        "SpatialDim": "USA",
        "TimeDim": 2020,
        "NumericValue": 78.0,
    }
    with patch("src.who_api_ingestion.fetch_data", return_value=[sample_record]), \
         patch("src.who_api_ingestion.OUTPUT_DIR", str(tmp_path)), \
         patch("src.who_api_ingestion.OUTPUT_FILE", str(tmp_path / "health.csv")):
        main()
    assert (tmp_path / "health.csv").exists()
