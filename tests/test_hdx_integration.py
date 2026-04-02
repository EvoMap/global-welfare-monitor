"""Tests for HDX dataset generation and publishing config."""

import os
import pandas as pd
from src.reporting.generate_hdx_datasets import generate_all, HDX_OUTPUT_DIR
from src.reporting.publish_hdx import DATASETS


def test_generate_all_with_data(tmp_path, monkeypatch):
    """generate_all should produce HXL files when source data exists."""
    data_dir = str(tmp_path / "data")
    os.makedirs(os.path.join(data_dir, "world_bank"))
    os.makedirs(os.path.join(data_dir, "who"))

    pd.DataFrame({"country": ["USA"], "year": [2022], "value": [1.0]}).to_csv(
        os.path.join(data_dir, "world_bank", "economic_indicators.csv"), index=False
    )
    pd.DataFrame({"country": ["USA"], "indicator": ["LE"], "value": [78]}).to_csv(
        os.path.join(data_dir, "who", "health_indicators.csv"), index=False
    )

    monkeypatch.setenv("DATA_DIR", data_dir)
    monkeypatch.setattr("src.reporting.generate_hdx_datasets.DATA_DIR", data_dir)
    hdx_out = str(tmp_path / "reports" / "hdx")
    monkeypatch.setattr("src.reporting.generate_hdx_datasets.HDX_OUTPUT_DIR", hdx_out)

    generated = generate_all()
    assert len(generated) >= 2
    for path in generated:
        assert os.path.exists(path)


def test_generate_all_no_data(tmp_path, monkeypatch):
    """generate_all should return empty list when no source data exists."""
    monkeypatch.setattr("src.reporting.generate_hdx_datasets.DATA_DIR", str(tmp_path))
    monkeypatch.setattr(
        "src.reporting.generate_hdx_datasets.HDX_OUTPUT_DIR",
        str(tmp_path / "hdx"),
    )
    generated = generate_all()
    assert generated == []


def test_dataset_configs_are_valid():
    """All dataset configs must have required fields."""
    for ds in DATASETS:
        assert "name" in ds
        assert "title" in ds
        assert "file" in ds
        assert "notes" in ds
        assert "tags" in ds
        assert len(ds["tags"]) > 0
        assert ds["name"].startswith("evomap-")
