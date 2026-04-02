"""Tests for data_ingestion.py -- verifies directory creation and file write."""

import os
import tempfile
from unittest.mock import patch

from src.data_ingestion import ingest_data


def test_ingest_creates_data_dir_if_missing():
    """Regression: ingest_data must create DATA_DIR before writing files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = os.path.join(tmpdir, "nonexistent_subdir")
        assert not os.path.exists(target)

        with patch("src.data_ingestion.DATA_DIR", target), \
             patch("src.data_ingestion.time.sleep"):
            ingest_data()

        assert os.path.isdir(target)
        assert os.path.isfile(os.path.join(target, "dummy_data.txt"))


def test_ingest_succeeds_when_dir_already_exists():
    """ingest_data should not fail when DATA_DIR already exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.data_ingestion.DATA_DIR", tmpdir), \
             patch("src.data_ingestion.time.sleep"):
            ingest_data()

        assert os.path.isfile(os.path.join(tmpdir, "dummy_data.txt"))
