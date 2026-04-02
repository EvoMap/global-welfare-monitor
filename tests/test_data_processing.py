"""Tests for data_processing.py -- verifies clean_and_transform_data pipeline."""

import pytest
import pandas as pd
import os
from src.data_processing import clean_and_transform_data


@pytest.fixture
def data_files(tmp_path):
    who_path = tmp_path / "who_data.csv"
    wb_path = tmp_path / "wb_data.csv"
    output_path = tmp_path / "output.csv"

    pd.DataFrame({
        "country": ["USA", "Canada"],
        "life_expectancy": [78, 82],
        "population": [330_000_000, 38_000_000],
    }).to_csv(who_path, index=False)

    pd.DataFrame({
        "country": ["USA", "Canada"],
        "gdp": [21_000_000, 1_700_000],
        "unemployment_rate": [4.0, 6.0],
    }).to_csv(wb_path, index=False)

    return str(who_path), str(wb_path), str(output_path)


def test_clean_and_transform_produces_csv(data_files):
    who_path, wb_path, output_path = data_files
    clean_and_transform_data(who_path, wb_path, output_path)
    assert os.path.exists(output_path)
    df = pd.read_csv(output_path)
    assert "country" in df.columns
    assert len(df) == 2


def test_clean_and_transform_merges_on_country(data_files):
    who_path, wb_path, output_path = data_files
    clean_and_transform_data(who_path, wb_path, output_path)
    df = pd.read_csv(output_path)
    assert "life_expectancy" in df.columns
    assert "gdp" in df.columns


def test_clean_and_transform_handles_missing_file(tmp_path):
    output_path = str(tmp_path / "output.csv")
    clean_and_transform_data("nonexistent.csv", "nonexistent2.csv", output_path)
    assert not os.path.exists(output_path)


def test_clean_and_transform_handles_na_values(tmp_path):
    who_path = tmp_path / "who.csv"
    wb_path = tmp_path / "wb.csv"
    output_path = tmp_path / "out.csv"

    pd.DataFrame({
        "country": ["USA", "Canada"],
        "life_expectancy": [78, "NA"],
    }).to_csv(who_path, index=False)

    pd.DataFrame({
        "country": ["USA", "Canada"],
        "gdp": [21_000_000, 1_700_000],
    }).to_csv(wb_path, index=False)

    clean_and_transform_data(str(who_path), str(wb_path), str(output_path))
    assert os.path.exists(str(output_path))
    df = pd.read_csv(str(output_path))
    assert len(df) == 2
