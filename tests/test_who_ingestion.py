import pytest
import pandas as pd
from unittest.mock import patch
from src import who_ingestion


def test_fetch_who_data_success(mock_api_response, mock_who_data):
    """Test successful fetching of WHO data."""
    with patch('requests.get') as mock_get:
        mock_get.return_value = mock_api_response(mock_who_data, 200)
        data = who_ingestion.fetch_who_data()
        assert data == mock_who_data


def test_fetch_who_data_failure(mock_api_response):
    """Test handling of API errors when fetching WHO data."""
    with patch('requests.get') as mock_get:
        mock_get.return_value = mock_api_response({}, 500)
        with pytest.raises(Exception):
            who_ingestion.fetch_who_data()


def test_transform_who_data(mock_who_data):
    """Test transformation of WHO data into a Pandas DataFrame."""
    df = who_ingestion.transform_who_data(mock_who_data)
    assert isinstance(df, pd.DataFrame)
    assert 'country' in df.columns
    assert 'year' in df.columns
    assert 'life_expectancy' in df.columns
    assert len(df) == len(mock_who_data)


def test_transform_who_data_empty_input():
    """Test transformation with empty input data."""
    df = who_ingestion.transform_who_data([])
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_load_who_data():
    """Test loading WHO data (currently a placeholder)."""
    df = pd.DataFrame({'country': ['USA'], 'year': [2020], 'life_expectancy': [77.0]})
    # In a real implementation, this would load data into a database or file.
    # For this test, we just check that the function runs without errors.
    who_ingestion.load_who_data(df)
    assert True # Placeholder assertion
