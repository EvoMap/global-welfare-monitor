""
import pytest
import pandas as pd
from src import water_access
import logging

# Suppress logging during tests
logging.disable(logging.CRITICAL)


@pytest.fixture
def mock_wash_data():
    """Fixture to provide mock WASH data."""
    return [
        {"country": "USA", "year": 2020, "indicator": "Improved water source (% of population with access)", "value": 95.0},
        {"country": "USA", "year": 2021, "indicator": "Improved water source (% of population with access)", "value": 95.5},
        {"country": "CAN", "year": 2020, "indicator": "Improved water source (% of population with access)", "value": 98.0},
        {"country": "CAN", "year": 2021, "indicator": "Improved water source (% of population with access)", "value": 98.5},
        {"country": "USA", "year": 2020, "indicator": "Water quality index", "value": 80.0},
        {"country": "USA", "year": 2021, "indicator": "Water quality index", "value": 81.0},
        {"country": "CAN", "year": 2020, "indicator": "Water quality index", "value": 85.0},
        {"country": "CAN", "year": 2021, "indicator": "Water quality index", "value": 86.0},
        {"country": "USA", "year": 2018, "indicator": "Improved water source (% of population with access)", "value": 94.0},
        {"country": "USA", "year": 2019, "indicator": "Improved water source (% of population with access)", "value": 94.5},
    ]


def test_parse_wash_data(mock_wash_data):
    """Test parsing WASH data."""
    df = water_access.parse_wash_data(mock_wash_data)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'country' in df.columns
    assert 'year' in df.columns
    assert 'indicator' in df.columns
    assert 'value' in df.columns
    assert df['year'].dtype == 'int64'
    assert df['value'].dtype == 'float64'


def test_parse_wash_data_empty_input():
    """Test parsing WASH data with empty input."""
    df = water_access.parse_wash_data([])
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_parse_wash_data_missing_columns():
    """Test parsing WASH data with missing columns."""
    data = [{"country": "USA", "year": 2020}]
    df = water_access.parse_wash_data(data)
    assert df.empty


def test_calculate_safe_water_coverage(mock_wash_data):
    """Test calculating safe water coverage."""
    df = water_access.parse_wash_data(mock_wash_data)
    coverage = water_access.calculate_safe_water_coverage(df, "USA")
    assert isinstance(coverage, float)
    assert 95.0 <= coverage <= 96.0


def test_calculate_safe_water_coverage_no_data():
    """Test calculating safe water coverage with no data for the region."""
    data = [{"country": "SOMEWHERE", "year": 2020, "indicator": "Improved water source (% of population with access)", "value": 95.0}]
    df = water_access.parse_wash_data(data)
    coverage = water_access.calculate_safe_water_coverage(df, "USA")
    assert coverage is None


def test_aggregate_water_quality_index(mock_wash_data):
    """Test aggregating water quality index."""
    df = water_access.parse_wash_data(mock_wash_data)
    index = water_access.aggregate_water_quality_index(df, "USA")
    assert isinstance(index, float)
    assert 80.0 <= index <= 81.0


def test_aggregate_water_quality_index_no_data():
    """Test aggregating water quality index with no data for the region."""
    data = [{"country": "SOMEWHERE", "year": 2020, "indicator": "Water quality index", "value": 80.0}]
    df = water_access.parse_wash_data(data)
    index = water_access.aggregate_water_quality_index(df, "USA")
    assert index is None


def test_project_trend(mock_wash_data):
    """Test projecting trend."""
    df = water_access.parse_wash_data(mock_wash_data)
    projected_value = water_access.project_trend(
        df, "USA", "Improved water source (% of population with access)", years=2
    )
    assert isinstance(projected_value, float)
    assert 96.0 <= projected_value <= 97.0


def test_project_trend_no_data():
    """Test projecting trend with no data."""
    data = [{"country": "SOMEWHERE", "year": 2020, "indicator": "Improved water source (% of population with access)", "value": 95.0}]
    df = water_access.parse_wash_data(data)
    projected_value = water_access.project_trend(
        df, "USA", "Improved water source (% of population with access)", years=2
    )
    assert projected_value is None


def test_project_trend_insufficient_data():
    """Test projecting trend with insufficient data points."""
    data = [{"country": "USA", "year": 2020, "indicator": "Improved water source (% of population with access)", "value": 95.0}]
    df = water_access.parse_wash_data(data)
    projected_value = water_access.project_trend(
        df, "USA", "Improved water source (% of population with access)", years=2
    )
    assert projected_value is None
""