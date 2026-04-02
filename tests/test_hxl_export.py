"""Tests for HXL-tagged CSV export."""

import pandas as pd
from src.reporting.hxl_export import to_hxl_csv


def test_to_hxl_csv_writes_tags(tmp_path):
    df = pd.DataFrame({
        "country": ["USA", "CAN"],
        "year": [2022, 2022],
        "value": [100.0, 200.0],
    })
    path = str(tmp_path / "test.hxl.csv")
    result = to_hxl_csv(df, path)
    assert result == path

    with open(path, "r") as f:
        lines = f.readlines()

    assert lines[0].strip() == "country,year,value"
    assert "#country+name" in lines[1]
    assert "#date+year" in lines[1]
    assert "#indicator+value+num" in lines[1]
    assert len(lines) == 4


def test_to_hxl_csv_custom_tags(tmp_path):
    df = pd.DataFrame({"region": ["Africa"], "pop": [1_400_000_000]})
    path = str(tmp_path / "custom.hxl.csv")
    tags = {"region": "#region+name", "pop": "#population+total"}
    to_hxl_csv(df, path, hxl_tags=tags)

    with open(path, "r") as f:
        lines = f.readlines()

    assert "#region+name" in lines[1]
    assert "#population+total" in lines[1]


def test_to_hxl_csv_empty(tmp_path):
    result = to_hxl_csv(pd.DataFrame(), str(tmp_path / "empty.csv"))
    assert result is None
