"""Tests for SDMX-CSV export."""

import pandas as pd
from src.reporting.sdmx_export import to_sdmx_csv, SDMX_COLUMNS, DATAFLOW_ID


def test_to_sdmx_csv_basic():
    df = pd.DataFrame({
        "country": ["USA", "CAN"],
        "indicator": ["GDP", "GDP"],
        "year": [2022, 2022],
        "value": [65000.0, 50000.0],
    })
    result = to_sdmx_csv(df)
    assert list(result.columns) == SDMX_COLUMNS
    assert len(result) == 2
    assert result["DATAFLOW"].iloc[0] == DATAFLOW_ID
    assert result["REF_AREA"].iloc[0] == "USA"
    assert result["OBS_STATUS"].iloc[0] == "A"


def test_to_sdmx_csv_writes_file(tmp_path):
    df = pd.DataFrame({
        "country": ["USA"],
        "indicator": ["POP"],
        "year": [2022],
        "value": [330_000_000],
    })
    path = str(tmp_path / "test.sdmx.csv")
    to_sdmx_csv(df, output_path=path)

    loaded = pd.read_csv(path)
    assert "DATAFLOW" in loaded.columns
    assert len(loaded) == 1


def test_to_sdmx_csv_empty():
    result = to_sdmx_csv(pd.DataFrame())
    assert result.empty


def test_to_sdmx_csv_with_unit_col():
    df = pd.DataFrame({
        "country": ["USA"],
        "indicator": ["TEMP"],
        "year": [2022],
        "value": [15.0],
        "unit": ["Celsius"],
    })
    result = to_sdmx_csv(df, unit_col="unit")
    assert result["UNIT_MEASURE"].iloc[0] == "Celsius"
