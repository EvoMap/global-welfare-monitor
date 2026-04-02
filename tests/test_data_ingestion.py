"""Tests for data_ingestion.py -- verifies pipeline orchestrator."""

import os
import tempfile
from unittest.mock import patch, MagicMock

from src.data_ingestion import ingest_data, _run_step


def test_ingest_creates_data_dir_if_missing():
    """Pipeline must create DATA_DIR before running steps."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = os.path.join(tmpdir, "nonexistent_subdir")
        assert not os.path.exists(target)

        with patch("src.data_ingestion.DATA_DIR", target):
            ingest_data(steps=[])

        assert os.path.isdir(target)


def test_ingest_runs_all_steps():
    """Pipeline should attempt every step and report results."""
    call_log = []

    def step_a():
        call_log.append("a")

    def step_b():
        call_log.append("b")

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.data_ingestion.DATA_DIR", tmpdir):
            results = ingest_data(steps=[("Step A", step_a), ("Step B", step_b)])

    assert call_log == ["a", "b"]
    assert results["Step A"] is True
    assert results["Step B"] is True


def test_ingest_continues_on_step_failure():
    """Pipeline should not abort when a step fails."""
    call_log = []

    def fail_step():
        raise RuntimeError("boom")

    def ok_step():
        call_log.append("ok")

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.data_ingestion.DATA_DIR", tmpdir):
            results = ingest_data(steps=[("Fail", fail_step), ("OK", ok_step)])

    assert results["Fail"] is False
    assert results["OK"] is True
    assert call_log == ["ok"]


def test_run_step_returns_true_on_success():
    assert _run_step("test", lambda: None) is True


def test_run_step_returns_false_on_failure():
    def bad():
        raise ValueError("oops")
    assert _run_step("test", bad) is False
