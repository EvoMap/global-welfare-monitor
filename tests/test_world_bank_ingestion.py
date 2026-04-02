"""Tests for world_bank_data_ingestion.py -- verifies reshaping logic."""

import pandas as pd
from unittest.mock import patch, MagicMock

from src.world_bank_data_ingestion import fetch_world_bank_data, save_data_to_csv


def _make_mock_wb_dataframe():
    """Build a DataFrame similar to what wb.data.DataFrame returns."""
    index = pd.MultiIndex.from_tuples(
        [("USA", 2022), ("CAN", 2022)],
        names=["economy", "time"],
    )
    return pd.DataFrame(
        {
            "NY.GDP.PCAP.CD": [65000.0, 50000.0],
            "SP.POP.TOTL": [330_000_000, 38_000_000],
        },
        index=index,
    )


def test_fetch_reshapes_correctly():
    """Result must have 'country' and 'year' columns, no MultiIndex."""
    mock_df = _make_mock_wb_dataframe()
    with patch("src.world_bank_data_ingestion.wb") as mock_wb:
        mock_wb.data.DataFrame.return_value = mock_df
        result = fetch_world_bank_data(["NY.GDP.PCAP.CD", "SP.POP.TOTL"])

    assert result is not None
    assert "country" in result.columns
    assert "year" in result.columns
    assert "economy" not in result.columns
    assert "time" not in result.columns
    assert len(result) == 2


def test_fetch_returns_none_on_api_error():
    """API errors should be caught and return None."""
    with patch("src.world_bank_data_ingestion.wb") as mock_wb:
        mock_wb.data.DataFrame.side_effect = Exception("API unavailable")
        result = fetch_world_bank_data(["NY.GDP.PCAP.CD"])

    assert result is None


def test_save_data_to_csv(tmp_path):
    """save_data_to_csv writes a valid CSV file."""
    df = pd.DataFrame({"country": ["USA"], "year": [2022], "value": [1.0]})
    filepath = str(tmp_path / "test_output.csv")
    save_data_to_csv(df, filepath)

    loaded = pd.read_csv(filepath)
    assert len(loaded) == 1
    assert list(loaded.columns) == ["country", "year", "value"]
